import pytest


async def graphql_request(client, query, cookies=None, variables=None):
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    resp = await client.post("/graphql", json=payload, cookies=cookies or {})
    print("GRAPHQL RESPONSE:", resp.json())
    return resp.json(), resp.cookies



@pytest.mark.asyncio
async def test_auth(client, state):
    query = """
    mutation {
      auth(username: "Yuki Nagato", password: "Snowbeauty") {
        __typename
        ... on AuthSuccess { message }
        ... on AuthError { message }
      }
    }
    """
    data, cookies = await graphql_request(client, query)
    assert data["data"]["auth"]["__typename"] == "AuthSuccess"

    state["cookies"] = cookies



@pytest.mark.asyncio
async def test_me(client, state):
    query = """
    query {
      me {
        __typename
        ... on SessionError { message }
        ... on UserType { id username isAdmin }
      }
    }
    """
    data, _ = await graphql_request(client, query, state["cookies"])
    assert data["data"]["me"]["__typename"] == "UserType"



@pytest.mark.asyncio
async def test_get_products(client, state):
    query = """
    query {
      products {
        result {
          id
          name
          description
          price
          amount
        }
      }
    }
    """
    data, _ = await graphql_request(client, query, state["cookies"])
    products = data["data"]["products"]["result"]
    assert isinstance(products, list)
    assert len(products) > 0

    state["product_id"] = products[0]["id"]



@pytest.mark.asyncio
async def test_get_product(client, state):
    query = f"""
    query {{
      getProduct(pid: "{state['product_id']}") {{
        __typename
        ... on ProductError {{ message }}
        ... on ProductResult {{
          result {{ id price name description amount }}
        }}
      }}
    }}
    """
    data, _ = await graphql_request(client, query, state["cookies"])
    assert data["data"]["getProduct"]["__typename"] == "ProductResult"



@pytest.mark.asyncio
async def test_add_to_cart(client, state):
    query = f"""
    mutation {{
      addToCart(productId: "{state['product_id']}", quantity: 1) {{
        __typename
        ... on SessionError {{ message }}
        ... on CartError {{ message }}
        ... on CartMessage {{ message }}
      }}
    }}
    """
    data, _ = await graphql_request(client, query, state["cookies"])
    assert data["data"]["addToCart"]["__typename"] == "CartMessage"



@pytest.mark.asyncio
async def test_get_cart(client, state):
    query = """
    query {
      getCart {
        __typename
        ... on SessionError { message }
        ... on CartError { message }
        ... on CartResult {
          result { userId productId quantity price }
        }
      }
    }
    """
    data, _ = await graphql_request(client, query, state["cookies"])
    assert data["data"]["getCart"]["__typename"] == "CartResult"



@pytest.mark.asyncio
async def test_place_order(client, state):
    query = """
    mutation {
      placeOrder {
        __typename
        ... on SessionError { message }
        ... on OrderResult {
          result { userId id status price }
        }
        ... on OrderError { message }
      }
    }
    """
    data, _ = await graphql_request(client, query, state["cookies"])
    assert data["data"]["placeOrder"]["__typename"] == "OrderResult"
    results = data["data"]["placeOrder"]["result"]
    assert isinstance(results, list) and len(results) > 0
    state["order_id"] = results[0]["id"]



@pytest.mark.asyncio
async def test_change_order_status(client, state):
    query = f"""
    mutation {{
      changeOrderStatus(orderId: "{state['order_id']}", newStatus: PAID) {{
        __typename
        ... on SessionError {{ message }}
        ... on OrderError {{ message }}
        ... on OrderResult {{
          result {{ id userId status }}
        }}
      }}
    }}
    """

    data, _ = await graphql_request(client, query, state["cookies"])
    assert data["data"]["changeOrderStatus"]["__typename"] == "OrderResult"
    assert data["data"]["changeOrderStatus"]["result"][0]["status"] == "Paid"


@pytest.mark.asyncio
async def test_get_orders(client, state):
    query = """
    query {
      getOrders {
        __typename
        ... on OrderResult {
          result {
            id
            status
            price
          }
        }
        ... on OrderError { message }
        ... on SessionError { message }
      }
    }
    """

    data, _ = await graphql_request(client, query, state["cookies"])

    typename = data["data"]["getOrders"]["__typename"]

    assert typename in ("OrderResult", "OrderError", "SessionError")

    if typename == "OrderResult":
        results = data["data"]["getOrders"]["result"]
        assert isinstance(results, list)
        assert all("id" in r for r in results)





@pytest.mark.asyncio
async def test_get_notifications(client, state):
    query = """
    query {
      getNotifications {
        __typename
        ... on NotificationReadResult {
          result{
            id
            status
          }
        }
        ... on SessionError {
          message
        }
      }
    }
    """
    data, _ = await graphql_request(client, query, state["cookies"])

    notifications = data["data"]["getNotifications"]['result']
    assert isinstance(notifications, list)
    assert len(notifications) > 0

    state["notif_id"] = notifications[0]["id"]


@pytest.mark.asyncio
async def test_read_notifications(client, state):
    query = f"""
    mutation {{
      readNotifications(notifIds: ["{state.get('notif_id', '')}"]) {{
        __typename
        ... on NotificationResult {{ message }}
        ... on SessionError {{ message }}
      }}
    }}
    """
    data, _ = await graphql_request(client, query, state["cookies"])

    message = data["data"]["readNotifications"]["message"]
    assert message == "Notifications read"

    query = """
    query {
        getNotifications {
            __typename
            ... on NotificationReadResult {
                result{
                    id
                    userId
                    orderId
                    status
              }
            }
            ... on SessionError {
              message
            }
        }
    }
    """
    data, _ = await graphql_request(client, query, state["cookies"])
    statuses = {n["id"]: n["status"] for n in data["data"]["getNotifications"]["result"]}
    assert statuses[state["notif_id"]] == "READ"

@pytest.mark.asyncio
async def test_logout(client, state):
    query = """
    mutation {
      logout {
        __typename
        ... on SessionError { message }
        ... on AuthSuccess { message }
      }
    }
    """
    data, _ = await graphql_request(client, query, state["cookies"])
    assert data["data"]["logout"]["__typename"] in ("AuthSuccess", "SessionError")

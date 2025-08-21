# GraphQL API Документация

Этот документ описывает использование GraphQL API для управления пользователями, продуктами, корзиной и заказами.

## 📋 Содержание
- [Аутентификация](#аутентификация)
- [Пользовательские данные](#пользовательские-данные)
- [Выход из системы](#выход-из-системы)
- [Работа с продуктами](#работа-с-продуктами)
- [Управление корзиной](#управление-корзиной)
- [Управление заказами](#управление-заказами)

---

## 🔐 Аутентификация

### Получение токена авторизации
```graphql
mutation Auth {
  auth(username: "Yuki Nagato", password: "Snowbeauty") {
    __typename
    ... on AuthSuccess {
      message
    }
    ... on AuthError {
      message
    }
  }
}
```
### Далее токен передаётся как
```graphql
{
  "authorization": "Bearer <session_id>"
}
```

---

## 👤 Пользовательские данные

### Получение информации о текущем пользователе
```graphql
query Me {
  me {
    __typename
    ... on SessionError {
      message
    }
    ... on UserType {
      id
      username
      isAdmin
      telegramHandler
    }
  }
}
```

---

## 🚪 Выход из системы

### Завершение сессии пользователя
```graphql
mutation Logout {
  logout {
    __typename
    ... on SessionError {
      message
    }
    ... on AuthSuccess {
      message
    }
  }
}
```

---

## 📦 Работа с продуктами

### Получение списка продуктов
```graphql
query GetProducts {
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
```

### Получение конкретного продукта
```graphql
query SingleProduct {
  getProduct(pid: "product_id") {
    __typename
    ... on ProductError {
      message
    }
    ... on ProductResult {
      result {
        id
        price
        name
        description
        amount
      }
    }
  }
}
```

---

## 🛒 Управление корзиной

### Просмотр корзины
```graphql
query GetCart {
  getCart {
    __typename
    ... on SessionError {
      message
    }
    ... on CartError {
      message
    }
    ... on CartResult {
      result {
        userId
        productId
        quantity
        price
      }
    }
  }
}
```

### Добавление товара в корзину
```graphql
mutation AddCart {
  addToCart(productId: "product_id", quantity: 5) {
    __typename
    ... on SessionError {
      message
    }
    ... on CartError {
      message
    }
    ... on CartMessage {
      message
    }
  }
}
```

### Удаление товара из корзины
```graphql
mutation RemoveCart {
  removeFromCart(productId: "product_id", quantity: 1) {
    __typename
    ... on SessionError {
      message
    }
    ... on CartError {
      message
    }
    ... on CartMessage {
      message
    }
  }
}
```

---

## 📦 Управление заказами

### Создание заказа
```graphql
mutation PlaceOrder {
  placeOrder {
    __typename
    ... on SessionError {
      message
    }
    ... on OrderResult {
      result {
        userId
        id
        status
        price
      }
    }
    ... on OrderError {
      message
    }
  }
}
```

### Изменение статуса заказа
```graphql
mutation ChangeOrderStatus {
  changeOrderStatus(orderId: "order_id", newStatus: "новый статус") {
    __typename
    ... on SessionError {
      message
    }
    ... on OrderError {
      message
    }
    ... on OrderResult {
      result {
        id
        userId
        status
      }
    }
  }
}
```

---

## 🎯 Примечания

- Для запросов, требующих авторизации, необходимо включить полученный токен в заголовки запроса
- Все ID полей (`pid`, `productId`, `orderId`) должны быть валидными идентификаторами
- Количество товара (`quantity`) должно быть положительным числом
- Статусы заказов должны соответствовать допустимым значениям в системе

## 🚀 Деплой

### 1) Предусловия
- Docker и Docker Compose установлены.
- Создайте файл окружения `app/settings/.env` (можно взять за основу `.env.example`)

### 2) Запуск инфраструктуры
```bash
docker compose up --build
```
для dev версии
```bash
docker compose -f docker-compose.yml up --build -d
```
для prod версии

### 3) Сидинг первичных данных в базу
```bash
docker compose exec app python -m app.db.seed
```
### 4) Запуск автотестов
```bash
docker compose run --rm app poetry install --with dev
```
```bash
docker compose run app poetry run pytest -v
```


# Документация API

## 📋 Содержание
- [Аутентификация](#аутентификация)
- [Пользовательские данные](#пользовательские-данные)
- [Выход из системы](#выход-из-системы)
- [Работа с продуктами](#работа-с-продуктами)
- [Управление корзиной](#управление-корзиной)
- [Управление заказами](#управление-заказами)

---

## 🔐 Аутентификация
### Регистрация
```graphql
mutation Register {
  register(username:"your_name", password:"your_password"){
    __typename
    ... on AuthSuccess{
      message
    }
  }
}
```
### Авторизация
```graphql
mutation Auth {
  auth(username: "Yuki Nagato", password: "Snowbeauty") {
    __typename
    ... on AuthSuccess {
      message
    }
  }
}
```


---

## 👤 Пользовательские данные

### Получение информации о текущем пользователе
```graphql
query Me {
  me {
    __typename
    ... on UserType {
      id
      username
      isAdmin
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
    ... on OrderResult {
      result {
        userId
        id
        status
        price
      }
    }
  }
}
```

### Изменение статуса заказа
- IN_PROCESS
- PAID
- SHIPPED
- DELIVERED
- CANCELED
```graphql
mutation ChangeOrderStatus {
  changeOrderStatus(orderId: "order_id", newStatus: "новый статус") {
    __typename
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

### Получить все заказы юзера
```graphql
query GetMyOrders {
  getOrders {
    ... on OrderResult {
      result {
        id
        status
        price
        }
      }
  }
}
```
### Получить один заказ
```graphql
query getOrder{
  getSingleOrder(orderId:"order_id"){
    __typename
    ... on OrderResult{
      result{
        price
        id
        status
      }
    }
  }
}
```
### Подписаться на изменения в заказах юзера
```graphql
subscription{
  orderStatusChanged{
    id
    userId
    status
  }
}
```

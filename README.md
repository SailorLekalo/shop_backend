## 🚀 Деплой

### 1) Предусловия
- Docker и Docker Compose установлены.
- Создайте файл окружения `app/settings/.env` (можно взять за основу `.env.example`) и заполните переменные:
  - `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_HOST`
  - `DATABASE_URL=postgresql+asyncpg://<user>:<pass>@<host>:5432/<db>`
  - `SESSION_EXPIRE_MINUTES` (например, `1440`)
  - `TELEGRAM_TOKEN` (опционально, если используете Telegram-уведомления)

> ⚠️ Не храните реальные секреты в репозитории. Добавьте `app/settings/.env` в `.gitignore`.

### 2) Запуск инфраструктуры
```bash
docker compose up -d db
```

### 3) Сидинг первичных данных в базу
```bash
docker compose exec app poetry run python -m app.db.seed
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

### Авторизация
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

# Тестовое задание на позицию Junior Python-разработчик. e504a06d28

## 👨 Автор: Федоров Дьулуур

## Реализовано

### Основные модули системы

### 1. Взаимодействие с пользователем

Позволяет пользователям регистрироваться, входить в систему, выходить из учетной записи, обновлять свои данные и удалять аккаунт.

* Регистрация: ввод имени (фамилии, отчества), email, пароля и подтверждения пароля.
* Обновление информации: пользователь может редактировать свой профиль.
* Удаление пользователя: удаление аккаунта реализовано как мягкое удаление — пользователь инициирует удаление, происходит logout, пользователь больше не может залогиниться, но при этом в базе учетная запись остается со статусом `is_active=False`.
* Login: пользователь входит в систему по email и паролю.
* Logout: пользователь выходит из системы.
* После login система при последующих обращениях идентифицирует пользователя по JWT-токену.

---

### 2. Система разграничения прав доступа

Реализована собственная система управления доступом (RBAC).

* Спроектирована схема управления доступами и описана в данном `README.md`.
* Реализованы соответствующие таблицы в базе данных.
* Таблицы заполнены тестовыми данными для демонстрации работы системы.
* Если пользователь имеет доступ к ресурсу — возвращается результат.
* Если пользователь не определён — возвращается `401 Unauthorized`.
* Если пользователь определён, но не имеет доступа — возвращается `403 Forbidden`.
* Реализован API для получения и изменения правил доступа пользователем с ролью администратора.

---

### 3. Минимальные бизнес-объекты

Реализованы mock-ресурсы:

* `products` — список продуктов
* CRUD операции для демонстрации RBAC
* Проверка owner-based доступа (доступ только к своим объектам)

---

## Архитектура

### Аутентификация

* Хеширование пароля через `bcrypt`

* Генерация JWT-токенов через `pyjwt`

* Используются:

  * access token
  * refresh token

* Передача токена:

```
Authorization: Bearer <access_token>
```

---

### Дополнительно реализовано

* Refresh token система
* Blacklist токенов при logout
* Проверка истечения токена
* Middleware для идентификации пользователя
* Проверка токена на blacklist

---

### Авторизация

Используется модель RBAC + расширения:

* **Роли**: `admin`, `user`
* **Ресурсы**: `products`, `access_rules`
* **Права**:

  * `read`
  * `create`
  * `update`
  * `delete`

Дополнительно:

* `read_all`
* `update_all`
* `delete_all`
* owner-based доступ

---

## Структура базы данных

### User

* `first_name`
* `last_name`
* `patronymic`
* `email`
* `password`
* `is_active`
* `role_id`

---

### Role

* `name`

---

### BusinessElement

* `name`

---

### AccessRule

* `role_id`
* `element_id`
* `can_read`
* `can_read_all`
* `can_create`
* `can_update`
* `can_update_all`
* `can_delete`
* `can_delete_all`

---

### RefreshToken

* `user`
* `token`
* `expires_at`
* `is_revoked`

---

### BlacklistedToken

* `token`

---

### Product (mock)

* `name`
* `description`
* `owner`

---

## Логика разграничения доступа

1. Пользователь - имеет роль
2. Роль - имеет набор правил (`AccessRule`)
3. Правило - привязано к ресурсу (`BusinessElement`)

Проверка:

* нет пользователя - `401`
* нет прав - `403`
* есть права - доступ

---

## Структура проекта

```
auth_system/
├── manage.py
├── auth_system/
│   ├── settings.py
│   ├── urls.py
│
├── core/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── auth.py
│   ├── permissions.py
│   ├── middleware.py
│   └── management/commands/seed_data.py
```

---

## Инструкция

### 1. Установка

```
git clone <repo>
cd auth_system
python -m venv env
```

---

### 2. Установка зависимостей

```
pip install django djangorestframework pyjwt bcrypt drf-spectacular
```

---

### 3. Миграции

```
python manage.py makemigrations
python manage.py migrate
```

---

### 4. Заполнение тестовыми данными

```
python manage.py seed_data
```

Создаётся:

* роли: `admin`, `user`
* ресурсы: `products`, `access_rules`
* пользователи:

```
admin@test.com / admin123
user@test.com / user123
```

---

### 5. Запуск

```
python manage.py runserver
```

---

## Swagger

```
http://127.0.0.1:8000/api/docs/
```

---

## API

### Регистрация

```
POST /api/register/
```

---

### Логин

```
POST /api/login/
```

Ответ:

```json
{
  "access_token": "...",
  "refresh_token": "..."
}
```

---

### Refresh token

```
POST /api/refresh/
```

---

### Logout

```
POST /api/logout/
```

---

### Профиль

```
PUT /api/profile/
DELETE /api/profile/delete/
```

---

### Продукты

```
GET /api/products/
POST /api/products/
PUT /api/products/{id}/
DELETE /api/products/{id}/
```

---

### Access Rules

```
GET /api/access-rules/
POST /api/access-rules/update/
```

---

## Обработка ошибок

* `401 Unauthorized`
* `403 Forbidden`
* `404 Not Found`
* `400 Bad Request`

---

## Как работает система

1. Пользователь логинится - получает JWT
2. Токен отправляется в каждом запросе
3. Middleware определяет пользователя
4. Проверяется роль
5. Проверяются права (`AccessRule`)
6. Возвращается результат или ошибка

---

## Требования ТЗ

* реализована собственная аутентификация
* реализована собственная авторизация
* описана схема RBAC
* реализованы таблицы
* добавлены тестовые данные
* реализованы ошибки 401 / 403
* реализован admin API
* реализованы mock-ресурсы

---

## Тестирование

* Swagger UI 
    - Нужна доработка по способу авторизации в самом сваггере
* curl

---

### 1. Регистрация

```bash
curl -X POST http://127.0.0.1:8000/api/register/ -H "Content-Type: application/json" -d "{\"first_name\":\"Ivan\",\"last_name\":\"Ivanov\",\"patronymic\":\"Ivanovich\",\"email\":\"user@test.com\",\"password\":\"123456\",\"password_confirm\":\"123456\"}"
```

---

### 2. Логин

```bash
curl -X POST http://127.0.0.1:8000/api/login/ -H "Content-Type: application/json" -d "{\"email\":\"user@test.com\",\"password\":\"123456\"}"
```

---

### 3. Обновление access token

```bash
curl -X POST http://127.0.0.1:8000/api/refresh/ -H "Content-Type: application/json" -d "{\"refresh_token\":\"REFRESH_TOKEN\"}"
```

---

### 4. Logout

```bash
curl -X POST http://127.0.0.1:8000/api/logout/ -H "Authorization: Bearer ACCESS_TOKEN" -H "Content-Type: application/json" -d "{\"refresh_token\":\"REFRESH_TOKEN\"}"
```

---

### 5. Обновление профиля

```bash
curl -X PUT http://127.0.0.1:8000/api/profile/ -H "Authorization: Bearer ACCESS_TOKEN" -H "Content-Type: application/json" -d "{\"first_name\":\"NewName\",\"last_name\":\"NewLastName\"}"
```

---

### 6. Удаление пользователя

```bash
curl -X DELETE http://127.0.0.1:8000/api/profile/delete/ -H "Authorization: Bearer ACCESS_TOKEN"
```

---

### 7. Получить список продуктов

```bash
curl -X GET http://127.0.0.1:8000/api/products/ -H "Authorization: Bearer ACCESS_TOKEN"
```

---

### 8. Создать продукт

```bash
curl -X POST http://127.0.0.1:8000/api/products/ -H "Authorization: Bearer ACCESS_TOKEN" -H "Content-Type: application/json" -d "{\"name\":\"Test Product\",\"description\":\"Test description\"}"
```

---

### 9. Обновить продукт

```bash
curl -X PUT http://127.0.0.1:8000/api/products/1/ -H "Authorization: Bearer ACCESS_TOKEN" -H "Content-Type: application/json" -d "{\"name\":\"Updated Product\"}"
```

---

### 10. Удалить продукт

```bash
curl -X DELETE http://127.0.0.1:8000/api/products/1/ -H "Authorization: Bearer ACCESS_TOKEN"
```

---

### 11. Получить правила доступа

```bash
curl -X GET http://127.0.0.1:8000/api/access-rules/ -H "Authorization: Bearer ADMIN_TOKEN"
```

---

### 12. Обновить правила доступа

```bash
curl -X POST http://127.0.0.1:8000/api/access-rules/update/ -H "Authorization: Bearer ADMIN_TOKEN" -H "Content-Type: application/json" -d "{\"role\":\"user\",\"resource\":\"products\",\"can_read\":true,\"can_read_all\":false,\"can_create\":true,\"can_update\":false,\"can_update_all\":false,\"can_delete\":false,\"can_delete_all\":false}"
```

---

### 401

```bash
curl http://127.0.0.1:8000/api/products/
```

---

### 403

```bash
curl -X DELETE http://127.0.0.1:8000/api/products/1/ -H "Authorization: Bearer USER_TOKEN"
```

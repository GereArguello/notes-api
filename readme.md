# 📝 Notes API

API RESTful para gestión de apuntes, construida con **FastAPI** y **SQLModel**.
Permite organizar información en una estructura jerárquica: **materias → temas → páginas → tags**, con autenticación segura basada en JWT.

---

## 🚀 Características

* 🔐 Autenticación con **Access + Refresh Tokens**
* 🔄 **Refresh Token Rotation + Revocación**
* 👤 Gestión completa de usuarios (CRUD + seguridad)
* 📚 Organización jerárquica:

  * Subjects (materias)
  * Topics (temas)
  * Pages (páginas)
  * Tags (etiquetas reutilizables)
* 📌 Sistema de orden (`sort_order`) con:

  * reordenamiento
  * consistencia automática
* 🏷️ Relación many-to-many entre páginas y tags
* 📊 Tracking de uso (`last_viewed_at`)
* 📄 Paginación en endpoints de listado
* 🧪 Test suite con **pytest**
* ⚙️ Configuración por variables de entorno

---

## 🧠 Modelo de datos

```
User
 └── Subject
      └── Topic
           └── Page
                └── Tags (many-to-many)
```

---

## 🔐 Autenticación

El sistema utiliza:

* `access_token` → para requests autenticados
* `refresh_token` → almacenado en cookie HTTP-only

### Flujo

1. Login → genera ambos tokens
2. Access token expira → usar `/auth/refresh`
3. Se rota el refresh token
4. Logout → revoca el token
5. Cambio de contraseña → revoca todas las sesiones

---

## ⚙️ Configuración

Crear archivo `.env` basado en `.env.example`:

```env
SECRET_KEY=tu_secret_key
DATABASE_URL=postgresql://user:password@localhost:5432/db_name

ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
REFRESH_TOKEN_GRACE_PERIOD=2

COOKIE_SECURE=False
ENVIRONMENT=development
DEBUG=True
```

---

## 🛠️ Instalación

```bash
git clone https://github.com/tu-usuario/notes-api.git
cd notes-api

python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

---

## ▶️ Ejecución

```bash
uvicorn app.main:app --reload
```

Swagger disponible en:

```
http://localhost:8000/docs
```

---

## 🧪 Tests

```bash
pytest
```

---

## 📌 Endpoints principales

### Auth

* `POST /auth/login`
* `POST /auth/refresh`
* `POST /auth/logout`

### Users

* `POST /users`
* `GET /users/me`
* `PATCH /users/me`
* `PATCH /users/me/password`
* `PATCH /users/me/deactivate`
* `DELETE /users/me`

### Subjects

* `POST /subjects`
* `GET /subjects`
* `GET /subjects/{id}`
* `PATCH /subjects/{id}`
* `DELETE /subjects/{id}`

### Topics

* `POST /subjects/{id}/topics`
* `GET /subjects/{id}/topics`
* `GET /subjects/{id}/topics/{id}`
* `PATCH /subjects/{id}/topics/{id}`
* `PATCH /subjects/{id}/topics/{id}/re-order`
* `DELETE /subjects/{id}/topics/{id}`

### Pages

* `POST /subjects/{id}/topics/{id}/pages`
* `GET /subjects/{id}/topics/{id}/pages`
* `GET /subjects/{id}/topics/{id}/pages/{id}`
* `PATCH /subjects/{id}/topics/{id}/pages/{id}`
* `PATCH /subjects/{id}/topics/{id}/pages/{id}/re-order`
* `DELETE /subjects/{id}/topics/{id}/pages/{id}`

### Tags

* `POST /subjects/{id}/topics/{id}/pages/{id}/tags`
* `GET /tags`
* `DELETE /subjects/{id}/topics/{id}/pages/{id}/tags/{id}`

---

## 🧩 Tecnologías

* FastAPI
* SQLModel
* PostgreSQL / SQLite
* Alembic
* JWT (python-jose)
* Pytest

---

## 🔒 Seguridad

* Passwords hasheados
* Refresh tokens persistidos y revocados
* Cookies HTTP-only
* Validación de ownership en todos los recursos

---

## 🎯 Estado del proyecto

✔ Backend completo
✔ Tests implementados
✔ Documentación de endpoints
⬜ Frontend (pendiente)

---

## 📌 Autor

**Geremias Arguello**

---

## 📄 Licencia

MIT

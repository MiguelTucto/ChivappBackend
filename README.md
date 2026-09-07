# Backend — MusicLink API (ChivApp)

API REST construida con **FastAPI** para la plataforma ChivApp. Expone recursos de usuarios, perfiles, reservas, contratos, pagos y notificaciones.

## Stack

| Tecnología | Uso |
|------------|-----|
| FastAPI 0.129 | Framework HTTP |
| SQLAlchemy 2.x | ORM |
| PostgreSQL | Base de datos |
| Pydantic v2 | Validación y schemas |
| python-jose + passlib | JWT y hashing de contraseñas |
| Uvicorn | Servidor ASGI |

## Estructura

```
app/
├── main.py                 # App FastAPI, CORS, create_all
├── api/
│   ├── deps.py             # get_db, get_current_user (cookie JWT)
│   └── v1/
│       ├── api.py          # Agregador de routers
│       └── endpoints/      # auth, profiles, bookings, ...
├── core/
│   ├── config.py           # Settings desde .env
│   ├── jwt.py              # Crear/decodificar tokens
│   └── hashing.py          # bcrypt
├── db/
│   └── session.py          # Engine y SessionLocal
├── models/                 # Tablas SQLAlchemy
└── schemas/                # Request/response Pydantic
```

## Variables de entorno

Copiar `.env.example` a `.env`:

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `SQLALCHEMY_DATABASE_URI` | URI PostgreSQL | `postgresql+psycopg2://user:pass@localhost:5432/musicdb` |
| `JWT_SECRET_KEY` | Secreto para firmar JWT | *(generar valor seguro)* |
| `JWT_ALGORITHM` | Algoritmo JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiración del token | `120` |
| `BACKEND_CORS_ORIGINS` | Orígenes permitidos (JSON array) | `["http://localhost:3000"]` |

## Arranque local

```bash
cd Backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Prefijo API: `/api/v1`

## Autenticación

- **Registro:** `POST /api/v1/auth/register` — roles: `contractor` | `musician`
- **Login:** `POST /api/v1/auth/login` — devuelve token y setea cookie `access_token`
- **Logout:** `POST /api/v1/auth/logout`
- **Usuario actual:** `GET /api/v1/auth/me` — requiere cookie

El token JWT incluye `sub` (user UUID) y `role`. Las rutas protegidas usan `get_current_user` leyendo la cookie.

## Modelo de datos

```
User (contractor | musician)
├── ContractorProfile (1:1)
└── MusicianProfile (1:1)
    ├── MusicianAvailability (1:N)
    └── MusicianMedia (1:N)

Booking (contractor ↔ musician)
├── Contract (1:1)
└── Payment (1:N)

Notification (por User)
```

### Estados de Booking

`requested` → `accepted` → `contract_pending` → `contract_signed` → `payment_pending` → `payment_retained` → `payment_released` → `completed` | `cancelled`

## Endpoints

### Auth — `/api/v1/auth`

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| POST | `/register` | No | Crear usuario |
| POST | `/login` | No | Login + cookie JWT |
| POST | `/logout` | No | Borrar cookie |
| GET | `/me` | Sí | Usuario autenticado |

### Profiles — `/api/v1/profiles`

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/musicians` | No | Listar músicos (paginado `skip`, `limit`) |
| GET | `/musicians/{id_or_slug}` | No | Perfil público de músico, por UUID o por `slug` |
| GET | `/musician/me` | Músico | Mi perfil |
| POST | `/musician` | Músico | Crear perfil |
| PUT | `/musician` | Músico | Actualizar perfil |
| GET | `/contractor/me` | Contratista | Mi perfil |
| POST | `/contractor` | Contratista | Crear perfil |
| PUT | `/contractor` | Contratista | Actualizar perfil |

### Musician Search — `/api/v1/musicians`

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| POST | `/search` | No | Búsqueda con filtros (ciudad, géneros, instrumentos, precio) |

### Bookings — `/api/v1/bookings`

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| POST | `/` | Contratista | Crear reserva |
| GET | `/` | Sí | Listar mis reservas |
| GET | `/{id}` | Sí | Detalle |
| PUT | `/{id}` | Contratista | Editar (solo `requested`) |
| POST | `/{id}/accept` | Músico | Aceptar |
| POST | `/{id}/cancel` | Sí | Cancelar |

### Contracts — `/api/v1/contracts`

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| POST | `/` | Contratista | Crear contrato |
| POST | `/{id}/sign/contractor` | Contratista | Firmar |
| POST | `/{id}/sign/musician` | Músico | Firmar |

### Payments — `/api/v1/payments`

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| POST | `/` | Contratista | Iniciar pago |
| POST | `/{id}/retain` | Sí | Retener fondos |
| POST | `/{id}/release` | Sí | Liberar fondos |

### Notifications — `/api/v1/notifications`

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/me` | Sí | Mis notificaciones |
| POST | `/` | — | *(removido — uso interno)* |
| POST | `/{id}/read` | Sí | Marcar leída |

### Availability — `/api/v1/availability`

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/me` | Músico | Listar franjas |
| POST | `/me` | Músico | Crear franja |
| PUT | `/me/{id}` | Músico | Actualizar |
| DELETE | `/me/{id}` | Músico | Eliminar |

### Media — `/api/v1/musicians/media`

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/me` | Músico | Listar media |
| POST | `/me` | Músico | Agregar |
| PUT | `/me/{id}` | Músico | Actualizar |
| DELETE | `/me/{id}` | Músico | Eliminar |

### Otros módulos (sin tabla de endpoints detallada)

| Módulo | Descripción |
|--------|-------------|
| `services/uniqueness.py` | Valida unicidad de email/teléfono/nombre artístico/documento; genera `slug` de URL único (`slugify` + sufijo incremental) |
| `services/availability_match.py` | Franjas de disponibilidad por día de semana, chequeo de solapamiento de horario |
| `services/booking_lifecycle.py`, `booking_location.py`, `booking_share.py` | Ciclo de vida de la reserva, ubicación en vivo, compartir por token |
| `services/booking_contract.py`, `contract_pdf.py` | Generación de contrato en PDF con firma (xhtml2pdf) |
| `services/platform_payment.py`, `settlement.py`, `payment_evidence.py` | Comisión de plataforma, retenciones/liberaciones, reembolsos por queja |
| `services/ratings.py` | Recalcula rating promedio de músico/contratista tras reseñas |
| `services/ensemble_members.py` | Invitación de integrantes de ensamble (crea usuario + perfil, setup de contraseña por token) |
| `services/email/` | Plantillas, renderer y envío de correos vía Resend |

No hay jobs en background (Celery/APScheduler/cron); todo corre síncrono dentro del request.

## Salud del servicio

`GET /health` (sin prefijo `/api/v1`) ejecuta un `SELECT 1` contra la base de datos y responde `200 {"status": "ok"}` o `503` si la DB no responde. Pensado como *readiness/liveness probe* para Cloud Run y como blanco de los smoke tests (ver más abajo).

## Base de datos y Migraciones (Alembic)

El proyecto utiliza **Alembic** para la gestión formal y versionada de migraciones en PostgreSQL.

> ⚠️ Los modelos usan tipos exclusivos de Postgres (`sqlalchemy.dialects.postgresql.UUID/JSONB/ARRAY`) en casi todas las tablas — no son compatibles con SQLite. Cualquier entorno de pruebas o desarrollo debe usar Postgres real.

### Crear base de datos

```sql
CREATE DATABASE musicdb;
```

### Comandos de Alembic

```bash
# Aplicar todas las migraciones pendientes (usar en CI/CD y despliegue a producción)
alembic upgrade head

# Ver la revisión actual aplicada en la base de datos
alembic current

# Ver el historial de migraciones
alembic history

# Generar una nueva migración automáticamente tras modificar modelos SQLAlchemy
alembic revision --autogenerate -m "descripcion_del_cambio"

# Revertir la última migración
alembic downgrade -1

# Marcar una base de datos existente como actualizada sin ejecutar DDL
alembic stamp head
```


## Testing

Suite de `pytest` en `tests/`, pensada para no requerir nada más que Postgres:

```bash
cd Backend
pip install -r requirements-dev.txt
pytest
```

- `tests/unit/` — lógica pura (slugify, matching de disponibilidad, cálculos de settlement/pricing). No requieren DB, siempre corren.
- `tests/integration/` — endpoints reales vía `TestClient` (registro, login, slug de músico). Marcados `@pytest.mark.db`; si no hay Postgres disponible en `TEST_DATABASE_URL` (por defecto `postgresql://postgres:postgres@localhost:5432/mariachi_test`), se saltan automáticamente con un mensaje claro en vez de fallar.
- `tests/smoke/` — pruebas de solo lectura contra un servidor **real ya corriendo** (local o desplegado). Se activan solo si se define `SMOKE_BASE_URL`:
  ```bash
  SMOKE_BASE_URL=https://api.tuapp.com pytest tests/smoke
  ```

CI en GitHub Actions (`.github/workflows/tests.yml`) corre `unit` + `integration` contra un contenedor de servicio Postgres en cada push/PR, y expone un job `smoke-tests` disparable a mano (`workflow_dispatch`) apuntando a la URL ya desplegada.

## Seguridad y Rate Limiting

La API implementa **Rate Limiting** mediante `slowapi` para mitigar ataques de fuerza bruta y abusos:
- `POST /api/v1/auth/login`: 10 req/min por IP.
- `POST /api/v1/auth/register`: 10 req/min por IP.
- `POST /api/v1/auth/forgot-password` y `/reset-password`: 5 req/min por IP.
- Respuestas de límite excedido: código HTTP `429 Too Many Requests` con cabecera `Retry-After`.

## Convenciones de código

- **Idioma API:** mensajes de error en español.
- **IDs:** UUID v4 en todas las entidades principales.
- **Roles:** enum `UserRole` — `contractor`, `musician`.
- **Schemas:** sufijos `Create`, `Update`, `Out` en Pydantic.

## Despliegue en GCP

- `GET /health` sirve como *health check* de Cloud Run (readiness/liveness).
- La app lee toda su configuración de variables de entorno (`app/core/config.py`, sin defaults para `SQLALCHEMY_DATABASE_URI` ni `JWT_SECRET_KEY`) — configúralas como variables de entorno o secretos de Cloud Run, no dependas del archivo `.env` en producción.
- Si la base es Cloud SQL, usar el conector correspondiente (Unix socket o Cloud SQL Auth Proxy) en `SQLALCHEMY_DATABASE_URI`.
- Después de cada despliegue, correr el job `smoke-tests` del workflow de CI apuntando a la URL real para confirmar que el servicio quedó sano.

## Notas técnicas

- Los helpers de autorización de bookings viven en `app/api/booking_helpers.py`.
- `POST /notifications/` fue removido del API público (uso interno futuro).
- En producción usar Alembic en lugar de `create_all()`.
- Todo `MusicianProfile` obtiene un `slug` único para URLs públicas (`/musicians/{slug}`), generado automáticamente al crearse (registro, invitación de ensamble) vía `app/services/uniqueness.py::next_available_musician_slug`. La búsqueda pública acepta UUID o slug indistintamente.

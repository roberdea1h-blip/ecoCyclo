# EcoCycle

Plataforma colaborativa para reportar y gestionar puntos de acumulación de residuos urbanos. Los ciudadanos reportan focos de basura con geolocalización y fotos, los voluntarios reclaman y limpian, y el sistema recompensa con puntos canjeables por recompensas.

## Características principales

- **Reportar residuos**: los usuarios pueden crear reportes con ubicación (mapa), fotos y tipo de residuo.
- **Reclamar tareas**: los voluntarios toman reportes activos para limpiarlos.
- **Verificación**: el reportero original confirma si la limpieza fue completada; puede rechazar con evidencia fotográfica.
- **Sistema de puntos**: cada reporte verificado otorga puntos al limpiador y al reportero.
- **Recompensas**: catálogo de recompensas canjeables con puntos acumulados.
- **Panel de administración**: gestión de usuarios, reportes, recompensas, tipos de residuo, canjes y configuración inicial.
- **Mapa interactivo**: visualización de reportes en mapa con Leaflet.
- **Notificaciones**: polling cada 30s para notificar eventos al usuario.

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python 3.12+, FastAPI, SQLAlchemy 2.0 (async), Pydantic v2 |
| Base de datos | PostgreSQL 17 |
| Cache / futuro | Redis 7 |
| Autenticación | JWT (access + refresh tokens en cookies HTTP-only), Argon2 |
| Migraciones | Alembic |
| Frontend | Vue 3 (Composition API, `<script setup>`), Pinia, Vue Router 5 |
| Estilos | TailwindCSS v4 (vía `@tailwindcss/vite`) |
| Mapas | Leaflet |
| Validación frontend | Zod |
| Empaquetado frontend | Vite 8 + Bun |
| Infraestructura | Docker Compose |
| Testing | pytest (async, httpx.AsyncClient, mocks) |

## Requisitos previos

- **Docker Desktop** (o Docker Engine + Docker Compose) para PostgreSQL y Redis
- **Python 3.12+**
- **Bun** (para el frontend)
- **Git**

## Estructura del proyecto

```
ecoCyclo/
├── docker-compose.yml        # PostgreSQL 17 + Redis 7
├── AGENTS.md                 # Notas para el agente opencode
├── uploads/                  # Imágenes subidas por los usuarios
├── ecoBack/                  # Backend — FastAPI
│   ├── app/
│   │   ├── api/v1/           # Rutas: auth, users, reports, rewards, admin, etc.
│   │   ├── core/             # Configuración (pydantic-settings), exception handlers
│   │   ├── db/               # Conexión a BD (SQLAlchemy async engine + session)
│   │   ├── models/           # Modelos SQLAlchemy (user, report, reward, role, etc.)
│   │   ├── repositories/     # Patrón repositorio (queries)
│   │   ├── schemas/          # Schemas Pydantic (request/response)
│   │   ├── services/         # Lógica de negocio
│   │   ├── storage/          # Manejo de archivos subidos
│   │   └── main.py           # Punto de entrada de la app
│   ├── alembic/              # Migraciones de base de datos
│   ├── tests/                # Tests unitarios e integración
│   ├── alembic.ini
│   ├── pytest.ini
│   └── requirements.txt
├── ecoFront/                 # Frontend — Vue 3 + Vite
│   ├── src/
│   │   ├── api/              # Clientes HTTP (axios wrapper)
│   │   ├── components/       # Componentes reutilizables
│   │   ├── composables/      # Lógica reactiva compartida
│   │   ├── router/           # Definición de rutas
│   │   ├── stores/           # Pinia stores (auth, reports, rewards, etc.)
│   │   ├── types/            # Tipos TypeScript
│   │   ├── utils/            # Utilidades
│   │   ├── views/            # Vistas/páginas
│   │   └── main.ts           # Punto de entrada
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
```

## Configuración del entorno

### 1. Infraestructura (Docker)

```bash
docker compose up -d
```

Esto levanta PostgreSQL 17 (puerto `5432`) y Redis 7 (puerto `6379`).

### 2. Variables de entorno

**`ecoBack/.env`**

```env
DATABASE_URL=postgresql+asyncpg://ecocycle_user:ecocycle_password@localhost:5432/ecocycle
SECRET_KEY=supersecretkeychangeinproduction
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
PROJECT_NAME=EcoCycle
API_V1_PREFIX=/api/v1
CORS_ORIGINS=["http://localhost:5173"]
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE=5242880
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=ecocycle_redis_password
REDIS_DB=0
```

**`ecoFront/.env`**

```env
VITE_API_URL=http://localhost:8000/api/v1
```

## Inicio rápido

### Backend

```bash
cd ecoBack

# Crear y activar un entorno virtual (opcional pero recomendado)
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones pendientes
alembic upgrade head

# Iniciar servidor de desarrollo (http://localhost:8000)
uvicorn app.main:app --reload
```

### Frontend

```bash
cd ecoFront

# Instalar dependencias
bun install

# Iniciar servidor de desarrollo (http://localhost:5173)
bun run dev
```

### Seed inicial

El sistema arranca sin datos. Para crear los roles (admin, user, moderator), el usuario administrador y 10 tipos de residuos, haz una petición `POST` al endpoint de setup:

```bash
curl -X POST http://localhost:8000/api/v1/admin/setup
```

Esto crea:

- **Roles**: `admin`, `user`, `moderator`
- **Admin**: `admin@ecocycle.app` / `admin123`
- **Tipos de residuo**: plástico, vidrio, papel/cartón, residuos orgánicos, residuos electrónicos, pilas/baterías, muebles/voluminosos, neumáticos, aceite usado, residuos de construcción/demolición

## Rutas del frontend

| Ruta | Vista | Descripción |
|---|---|---|
| `/login` | LoginView | Inicio de sesión |
| `/register` | RegisterView | Registro de usuario |
| `/dashboard` | DashboardView | Panel principal: mapa, tareas activas, estadísticas |
| `/reports` | ReportsView | Lista de todos los reportes con filtros |
| `/reports/create` | ReportCreateView | Crear un nuevo reporte |
| `/reports/:id` | ReportDetailView | Detalle de un reporte |
| `/rewards` | RewardsView | Catálogo de recompensas y canje |
| `/notifications` | NotificationsView | Historial de notificaciones |
| `/profile` | ProfileView | Perfil del usuario con historial de actividad |
| `/admin` | AdminView | Panel de administración (solo admin) |

## Comandos útiles

### Backend (ejecutar desde `ecoBack/`)

| Comando | Descripción |
|---|---|
| `uvicorn app.main:app --reload` | Servidor de desarrollo (puerto 8000) |
| `pytest` | Todos los tests |
| `pytest tests -m unit` | Tests unitarios rápidos (DB mockeada) |
| `pytest tests -m integration` | Tests de integración (dependencias mockeadas) |
| `pytest tests/test_auth.py::test_name` | Test individual |
| `alembic revision --autogenerate -m "mensaje"` | Crear migración automática |
| `alembic upgrade head` | Aplicar migraciones pendientes |

### Frontend (ejecutar desde `ecoFront/`)

| Comando | Descripción |
|---|---|
| `bun run dev` | Servidor de desarrollo (puerto 5173) |
| `bun run build` | Build de producción en `dist/` |
| `bun run preview` | Vista previa del build de producción |

## Testing

- Los tests usan `httpx.AsyncClient` con `ASGITransport` (no levantan un servidor real).
- La base de datos se mockea con `MagicMock`/`AsyncMock` — **no se necesita una base de datos de pruebas**.
- `conftest.py` sobreescribe `DATABASE_URL` a `sqlite+aiosqlite:///:memory:` para que el engine nunca intente conectar a PostgreSQL real.
- `session.py` auto-commitea en éxito, auto-rollbackea en excepción.
- Dos categorías de tests:
  - `unit`: rápidos, sin base de datos
  - `integration`: ciclo completo request/response con dependencias mockeadas

>> ## Notas de arquitectura

- **Autenticación**: JWT access + refresh tokens almacenados en cookies HTTP-only. El access token también se acepta vía header `Authorization: Bearer` como fallback.
- **Hash de contraseñas**: Argon2 (vía `argon2-cffi`), no bcrypt.
- **JWT**: Se usa `python-jose` (no `PyJWT`).
- **Patrón repositorio**: `repositories/` ejecutan queries, `services/` contienen lógica de negocio, las rutas son delgadas.
- **Filtro espacial**: la distancia haversine se calcula en Python (no en SQL) sobre `lat`/`lng`/`radius_km`.
- **Subida de imágenes**: almacenamiento local en `uploads/`, servido via `StaticFiles` en `/uploads`.

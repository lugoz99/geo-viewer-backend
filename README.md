# Geo Viewer Platform

Una plataforma de visualización geoespacial construida con **FastAPI**, **SQLAlchemy** y **PostGIS**. Soporta datos geoespaciales, autenticación y APIs RESTful para aplicaciones de mapas.

## 🚀 Características

- **API RESTful** con FastAPI.
- **Base de datos geoespacial** con PostGIS.
- **Autenticación JWT** con bcrypt.
- **Migraciones** con Alembic.
- **Desarrollo híbrido**: App local + BD en Docker.
- **Despliegue** con Docker Compose.

## 📋 Requisitos

- **Python 3.13+**
- **Docker & Docker Compose**
- **uv** (gestor de dependencias moderno)

## ⚙️ Configuración Inicial

### 1. Clona el repositorio
```bash
git clone <url-del-repo>
cd geo-viewer-platform
```

### 2. Variables de entorno
Elige el archivo de entorno según tu setup:

- **Desarrollo local**: Copia `.env.development` a `.env`
  ```bash
  cp .env.development .env
  ```
  (Ya tiene valores de ejemplo para desarrollo).

- **Producción**: Copia `.env.production` a `.env` y edita los valores comentados.
  ```bash
  cp .env.production .env
  # Edita .env con valores reales
  ```

**Importante**: Cambia `POSTGRES_HOST` según el entorno:
- Desarrollo: `localhost` (BD en Docker, app local).
- Producción: `db` (ambos en contenedores).

Ejemplo de `.env` para desarrollo (ya en `.env.development`):
```env
POSTGRES_DB=geovisor_dev
POSTGRES_USER=geovisor_user
POSTGRES_PASSWORD=dev_password_123
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DATABASE_URL=postgresql+asyncpg://geovisor_user:dev_password_123@localhost:5432/geovisor_dev
API_PORT=8000
SECRET_KEY=dev_secret_key_change_in_production_123456789
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENVIRONMENT=development
```

### 3. Instala dependencias
```bash
uv sync
```
Esto crea un entorno virtual (`.venv`) con todas las librerías.

## 🛠️ Desarrollo Local

Enfoque híbrido: **App corriendo localmente** con dependencias instaladas, **BD en contenedor Docker**. Esto permite desarrollo rápido con IntelliSense y recarga automática.

### Levantar la BD
```bash
make local-db  # O: docker-compose up db -d
```
Levanta PostGIS en background. Verifica con `docker-compose logs db`.

### Correr la app
```bash
make local-run  # O: uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- Accede a `http://localhost:8000/health` para probar.
- La app se recarga automáticamente al editar código.
- Conecta a la BD usando las variables de `.env`.

### Migraciones de BD
```bash
make local-migrate     # Aplicar migraciones: uv run alembic upgrade head
make local-migration name="tu_mensaje"  # Crear nueva migración
```

### Otros comandos útiles
- `make db-shell` - Acceder a psql en el contenedor de BD.
- `make logs-db` - Ver logs de la BD.
- `uv run pytest` - Ejecutar tests.

## 🐳 Despliegue con Docker

Para producción o entornos completos, usa Docker Compose para todo (app + BD).

### Construir y levantar
```bash
make build  # Primera vez: docker-compose up -d --build
make up     # Las demás veces: docker-compose up -d
```

### Verificar
```bash
make logs   # Ver logs de la API
curl http://localhost:8000/health
```

### Migraciones en contenedor
```bash
make migrate  # Aplicar: docker-compose exec api uv run alembic upgrade head
```

### Parar y limpiar
```bash
make down    # Parar contenedores
make clean   # Parar y borrar volúmenes (¡cuidado, borra datos!)
```

## 📁 Estructura del Proyecto

```
geo-viewer-platform/
├── app/                    # Código de la aplicación
│   ├── main.py            # Punto de entrada FastAPI
│   ├── config/            # Configuración (Pydantic settings)
│   ├── database/          # Conexión a BD
│   ├── models/            # Modelos SQLAlchemy
│   ├── schemas/           # Esquemas Pydantic
│   ├── services/          # Lógica de negocio
│   └── utils/             # Utilidades
├── test/                  # Tests
├── alembic/               # Migraciones de BD
├── docker-compose.yaml    # Config Docker
├── Dockerfile             # Imagen de la app
├── pyproject.toml         # Dependencias y config
├── Makefile               # Comandos automatizados
├── .env.development       # Variables para desarrollo
├── .env.production        # Variables para producción (comentadas)
├── .env_example           # Ejemplo genérico
└── README.md              # Este archivo
```

## 🔧 Comandos del Makefile

### Desarrollo Local
- `make local-db` - Levantar BD en background.
- `make local-run` - Correr app localmente.
- `make local-migrate` - Aplicar migraciones locales.
- `make local-migration name="msg"` - Crear migración local.

### Docker Completo
- `make build` - Construir y levantar con rebuild.
- `make up` - Levantar contenedores.
- `make down` - Parar contenedores.
- `make logs` - Logs de la API.
- `make logs-db` - Logs de la BD.
- `make shell` - Shell en contenedor de API.
- `make db-shell` - Shell psql en BD.
- `make migrate` - Migraciones en contenedor.
- `make migration name="msg"` - Crear migración en contenedor.
- `make clean` - Limpiar volúmenes.

## 🧪 Tests

```bash
uv run pytest
```

## 📚 APIs Disponibles

- `GET /health` - Verificar estado de la app.

*(Agrega más endpoints aquí según desarrolles la app)*

## 🤝 Contribución

1. Crea una rama para tu feature.
2. Escribe tests.
3. Corre `uv run ruff check` y `uv run black` para linting.
4. Haz commit y push.
5. Abre un PR.

## 📄 Licencia

[Tu licencia aquí, ej. MIT]

---

¡Disfruta desarrollando con Geo Viewer Platform! Si tienes dudas, revisa los logs o abre un issue.
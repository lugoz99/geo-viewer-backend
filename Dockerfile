FROM python:3.13-slim

WORKDIR /app

# Instalar uv
RUN pip install uv

# Copiar dependencias primero para aprovechar cache de Docker
COPY pyproject.toml uv.lock ./

# Instalar dependencias sin las de desarrollo
RUN uv sync --no-dev --no-install-project

# Copiar el resto del codigo
COPY . .

# Instalar el proyecto
RUN uv sync --no-dev

# Comando para produccion
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
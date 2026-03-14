import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

from app.database.db import get_async_engine


async def test_connection():
    print("Obteniendo engine...")
    engine = get_async_engine()

    print("Intentando conectar...")
    try:
        async with engine.connect() as conn:
            print("¡Conexión exitosa!")
            result = await conn.execute("SELECT 1")
            print(f"Resultado: {result.scalar()}")
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_connection())

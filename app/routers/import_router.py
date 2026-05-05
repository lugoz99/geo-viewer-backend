"""
Router de importación SIMPLE (compatible con ImportService actual)

- Solo soporta auto-import (GeoJSON, KML, CSV con coords)
- NO usa usuarios
- NO usa mapping
- NO usa execute separado
"""

import os
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.import_service import ImportService
from app.database.db import get_db
from app.schemas.import_ import ImportResponse
from app.exceptions.request_exception import ValidationError, DatabaseError
from app.utils.import_utils import get_file_type, validate_file_size

# Config
UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

router = APIRouter(prefix="/api/v1/imports", tags=["imports"])


@router.post(
    "/upload",
    response_model=ImportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_file(
    file: UploadFile = File(...),
    project_id: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Sube archivo y lo importa directamente.

    Compatible con:
    - GeoJSON
    - KML
    - CSV con lat/lon

    NO hay mapping ni pasos adicionales.
    """
    print("ESTOY_AQUI")
    # ── Validar archivo ─────────────────────────────
    if not file.filename:
        raise ValidationError("Archivo sin nombre")

    file_type = get_file_type(file.filename)
    if not file_type:
        raise ValidationError(
            "Formato no soportado",
            details={"allowed": ["geojson", "kml", "csv"]},
        )

    # ── Validar project_id ─────────────────────────
    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise ValidationError("project_id inválido")

    # ── Guardar archivo temporal ───────────────────
    UPLOAD_DIR.mkdir(exist_ok=True)
    temp_path = UPLOAD_DIR / f"{uuid.uuid4()}_{file.filename}"

    try:
        content = await file.read()

        valid, msg = validate_file_size(len(content), MAX_FILE_SIZE)
        if not valid:
            raise ValidationError(msg)

        with open(temp_path, "wb") as f:
            f.write(content)

        # ── Llamar service ───────────────────────────
        service = ImportService(db)

        result = await service.analyze_file(
            file_path=str(temp_path),
            file_name=file.filename,
            file_type=file_type,
            project_id=project_uuid,
        )

        # ── Respuesta ───────────────────────────────
        if "layer_id" in result:
            return ImportResponse(
                success=True,
                status="completed",
                import_id=result["file_import_id"],
                layer_id=result["layer_id"],
                features_imported=0,  # tu service no lo devuelve
                message="Importación completada",
            )

        else:
            return ImportResponse(
                success=False,
                status="failed",
                import_id=None,
                message=result.get("error", "Error desconocido"),
            )

    except ValidationError:
        raise
    except Exception as e:
        raise DatabaseError(
            message="Error al procesar archivo",
            details={"error": str(e)},
        )

    finally:
        if temp_path.exists():
            os.remove(temp_path)


# ─────────────────────────────────────────────
# LISTAR IMPORTS (simple, sin user)
# ─────────────────────────────────────────────


@router.get("")
async def list_imports(db: AsyncSession = Depends(get_db)):
    """
    Lista todas las importaciones (simple).
    """
    service = ImportService(db)
    imports = await service.list_imports()

    return [
        {
            "id": imp.id,
            "status": imp.status.value,
            "file_name": imp.file_name,
            "layer_id": imp.layer_id,
            "started_at": str(imp.started_at) if imp.started_at else None,
            "finished_at": str(imp.finished_at) if imp.finished_at else None,
            "error": imp.error_log,
        }
        for imp in imports
    ]

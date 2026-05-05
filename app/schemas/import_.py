"""
Schemas para importación de archivos geoespaciales.

Define los modelos de request/response para los endpoints de importación:
- Upload: subir archivo y analizar
- Mapping: confirmar mapeo de columnas (CSV/Excel)
- Execute: ejecutar importación
- Status: consultar estado de importación
"""

from enum import Enum
from typing import Optional
from uuid import UUID

from app.schemas.custom_base import CustomBase


# ────────────────────────────────────────────────────────────────────
# ENUMS
# ────────────────────────────────────────────────────────────────────

class FileType(str, Enum):
    """Tipos de archivo soportados."""
    GEOJSON = "geojson"
    KML = "kml"
    CSV = "csv"
    EXCEL = "excel"


class ImportStatus(str, Enum):
    """Estados posibles de una importación."""
    PENDING = "pending"
    PROCESSING = "processing"
    NEEDS_MAPPING = "needs_mapping"
    COMPLETED = "completed"
    FAILED = "failed"


# ────────────────────────────────────────────────────────────────────
# REQUEST SCHEMAS
# ────────────────────────────────────────────────────────────────────

class ImportMappingRequest(CustomBase):
    """
    Body para POST /imports/{id}/mapping.

    El usuario envía esto cuando el archivo requiere mapeo de columnas.
    Ejemplo para CSV con coordenadas ambiguas:

    {
        "geometry_type": "point",
        "latitude": "coord_y",
        "longitude": "coord_x",
        "attributes": {
            "nombre": "nom_establecimiento",
            "tipo": "tipo_instalacion"
        }
    }
    """
    geometry_type: str  # "point", "linestring", "polygon"
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    wkt_column: Optional[str] = None
    attributes: dict = {}

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "geometry_type": "point",
                    "latitude": "LATITUDE",
                    "longitude": "LONGITUDE",
                    "attributes": {"nombre": "NOMBRE", "tipo": "TIPOLOGIA"}
                },
                {
                    "geometry_type": "polygon",
                    "wkt_column": "GEOMETRY_WKT",
                    "attributes": {"area": "AREA", "nombre": "NOMBRE"}
                }
            ]
        }


# ────────────────────────────────────────────────────────────────────
# RESPONSE SCHEMAS
# ────────────────────────────────────────────────────────────────────

class ImportAnalysisResult(CustomBase):
    """
    Resultado del análisis inicial del archivo.

    Se devuelve cuando el archivo requiere mapeo (needs_mapping).
    Contiene información sobre qué se detectó y sugerencias de mapeo.

    Ejemplo para CSV:
    {
        "file_type": "csv",
        "total_rows": 500,
        "columns": ["ID", "nombre", "coord_a", "coord_b"],
        "geometry_detected": null,
        "suggested_mapping": {
            "latitude": "coord_b",
            "longitude": "coord_a"
        }
    }

    Ejemplo para KML con folders:
    {
        "file_type": "kml",
        "folders": ["zonas_nario"],
        "geometry_detected": "polygon",
        "attribute_fields": ["NOMBRE", "AREA", ...]
    }
    """
    file_type: str
    columns: Optional[list[str]] = None
    folders: Optional[list[str]] = None
    sheets: Optional[list[str]] = None
    geometry_detected: Optional[str] = None
    attribute_fields: Optional[list[str]] = None
    total_rows: Optional[int] = None
    suggested_mapping: Optional[dict] = None


class ImportResponse(CustomBase):
    """
    Respuesta genérica de los endpoints de importación.

    Para auto-importable (GeoJSON/KML simple):
    {
        "success": true,
        "status": "completed",
        "import_id": "uuid",
        "layer_id": "uuid",
        "features_imported": 150
    }

    Para necesita mapeo (CSV ambiguo):
    {
        "success": true,
        "status": "needs_mapping",
        "import_id": "uuid",
        "analysis": {...}
    }
    """
    success: bool
    status: str
    import_id: UUID
    message: str
    layer_id: Optional[UUID] = None
    features_imported: Optional[int] = None
    analysis: Optional[ImportAnalysisResult] = None


class ImportStatusResponse(CustomBase):
    """
    Respuesta para GET /imports/{id}.

    Muestra el estado actual, progreso y resultados de la importación.
    """
    import_id: UUID
    status: str
    progress: int
    file_name: str
    file_type: str
    total_rows: Optional[int] = None
    features_imported: int = 0
    features_failed: int = 0
    layer_ids: Optional[list[UUID]] = None
    error_log: Optional[dict] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None

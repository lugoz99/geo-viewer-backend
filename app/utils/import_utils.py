"""
Utilidades para importación de archivos geoespaciales.

Funciones puras y helpers que no dependen de BD ni servicios.
"""

from app.schemas.import_ import FileType


def get_file_type(file_name: str) -> FileType | None:
    """
    Detecta el tipo de archivo desde la extensión.

    Ejemplo:
        'pasto.kml' → FileType.KML
        'datos.xlsx' → FileType.EXCEL
        'documento.txt' → None
    """
    ext = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""

    mapping = {
        "geojson": FileType.GEOJSON,
        "json": FileType.GEOJSON,
        "kml": FileType.KML,
        "kmz": FileType.KML,
        "csv": FileType.CSV,
        "xlsx": FileType.EXCEL,
        "xls": FileType.EXCEL,
    }
    return mapping.get(ext)


def validate_file_size(file_size: int, max_size: int) -> tuple[bool, str]:
    """
    Valida que el tamaño del archivo no exceda el máximo permitido.

    Returns:
        (is_valid, message)
    """
    if file_size > max_size:
        max_mb = max_size // (1024 * 1024)
        return False, f"Archivo demasiado grande. Máximo: {max_mb}MB"
    return True, ""


def get_supported_formats() -> list[str]:
    """Retorna lista de extensiones soportadas."""
    return ["geojson", "json", "kml", "kmz", "csv", "xlsx", "xls"]

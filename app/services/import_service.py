"""
Servicio de importación de archivos geoespaciales.
VERSIÓN SIN USUARIOS (sin created_by)
"""

import uuid
import numpy as np
from typing import Any
from datetime import datetime

import geopandas as gpd
import pandas as pd
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.models.file_import import FileImport, ImportStatus
from app.models import Layer, Feature
from app.models.Layer import GeometryType
from app.models.project import Project
from app.schemas.import_ import FileType, ImportAnalysisResult
from app.exceptions.request_exception import NotFoundError
from app.utils.logging import get_logger

logger = get_logger(__name__)

LATITUDE_KEYWORDS = ["lat", "latitude", "latitud", "y", "coord_y"]
LONGITUDE_KEYWORDS = ["lon", "lng", "longitude", "longitud", "x", "coord_x"]


def _detect_column(columns: list[str], keywords: list[str]) -> str | None:
    cols_lower = {col.lower(): col for col in columns}
    for keyword in keywords:
        if keyword in cols_lower:
            return cols_lower[keyword]
    return None


def _create_point_gdf(df: pd.DataFrame, lon_col: str, lat_col: str):
    return gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df[lon_col], df[lat_col]),
        crs="EPSG:4326",
    )


def _detect_geometry_from_keywords(columns: list[str]):
    lat = _detect_column(columns, LATITUDE_KEYWORDS)
    lon = _detect_column(columns, LONGITUDE_KEYWORDS)
    if lat and lon:
        return {"latitude": lat, "longitude": lon}
    return None


class ImportService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def validate_project_exists(self, project_id: uuid.UUID) -> Project:
        result = await self.db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        if not project:
            raise NotFoundError("Proyecto no encontrado")
        return project

    async def analyze_file(
        self,
        file_path: str,
        file_name: str,
        file_type: FileType,
        project_id: uuid.UUID,
    ) -> dict[str, Any]:

        await self.validate_project_exists(project_id)

        file_import = FileImport(
            id=uuid.uuid4(),
            project_id=project_id,
            file_name=file_name,
            file_type=file_type.value,
            status=ImportStatus.PROCESSING,
            started_at=datetime.utcnow(),
        )
        self.db.add(file_import)
        await self.db.flush()

        try:
            if file_type == FileType.GEOJSON:
                gdf = await run_in_threadpool(gpd.read_file, file_path)
            elif file_type == FileType.KML:
                gdf = await run_in_threadpool(gpd.read_file, file_path)
            elif file_type == FileType.CSV:
                df = await run_in_threadpool(pd.read_csv, file_path)
                mapping = _detect_geometry_from_keywords(df.columns)
                if not mapping:
                    return await self._fail(file_import, "No coords")
                gdf = await run_in_threadpool(
                    _create_point_gdf, df, mapping["longitude"], mapping["latitude"]
                )
            else:
                return await self._fail(file_import, "Formato no soportado")

            return await self._auto_import(gdf, file_import)

        except Exception as e:
            return await self._fail(file_import, str(e))

    async def _auto_import(self, gdf, file_import):

        if gdf.crs is None:
            gdf = gdf.set_crs("EPSG:4326")

        geom_type = gdf.geom_type.mode().iloc[0]

        layer = Layer(
            project_id=file_import.project_id,
            name=file_import.file_name,
            geometry_type=self._parse_geom(geom_type),
            srid=4326,
        )

        self.db.add(layer)
        await self.db.flush()

        data = []
        for _, row in gdf.iterrows():
            data.append(
                {"layer_id": layer.id, "geom": row.geometry.wkt, "attributes": {}}
            )

        await self.db.execute(insert(Feature), data)

        file_import.status = ImportStatus.COMPLETED
        file_import.layer_id = layer.id
        file_import.finished_at = datetime.utcnow()

        await self.db.commit()

        return {"layer_id": layer.id, "file_import_id": file_import.id}

    def _parse_geom(self, g):
        g = g.lower()
        if "point" in g:
            return GeometryType.POINT
        if "line" in g:
            return GeometryType.LINESTRING
        if "polygon" in g:
            return GeometryType.POLYGON
        raise ValueError("geom desconocida")

    async def _fail(self, file_import, error):
        file_import.status = ImportStatus.FAILED
        file_import.error_log = {"error": error}
        await self.db.commit()
        return {"error": error}

    async def list_imports(self):
        result = await self.db.execute(select(FileImport))
        return result.scalars().all()

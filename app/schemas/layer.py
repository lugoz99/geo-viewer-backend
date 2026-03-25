import uuid
from app.schemas.custom_base import CustomBase


class LayerCreate(CustomBase):
    project_id: uuid.UUID
    created_by: uuid.UUID
    name: str
    description: str | None = None
    geometry_type: str
    style: dict | None = None
    filters: dict | None = None
    attribute_schema: dict | None = None
    visible: bool = True
    z_index: int = 0
    status: str = "active"
    is_derived: bool = False
    parent_layer_id: uuid.UUID | None = None
    geoprocess_type: str | None = None


class LayerUpdate(CustomBase):
    """Schema para actualizar capa (todos los campos opcionales)"""

    name: str | None = None
    description: str | None = None
    style: dict | None = None
    filters: dict | None = None
    attribute_schema: dict | None = None
    visible: bool | None = None
    z_index: int | None = None
    status: str | None = None


class LayerResponse(CustomBase):
    id: uuid.UUID
    project_id: uuid.UUID
    created_by: uuid.UUID
    name: str
    description: str | None = None
    geometry_type: str
    style: dict | None = None
    filters: dict | None = None
    attribute_schema: dict | None = None
    visible: bool
    z_index: int
    status: str
    is_derived: bool
    parent_layer_id: uuid.UUID | None = None
    geoprocess_type: str | None = None
    feature_count: int

from sqlalchemy.orm import mapped_column, Mapped
from app.database.db import Base
from geoalchemy2 import Geometry
import datetime


class Test(Base):
    __tablename__ = "test"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    name_full: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    created_at: Mapped[datetime.datetime]

    # PostGIS geometry column (point, EPSG:4326)
    location: Mapped[str] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=True
    )

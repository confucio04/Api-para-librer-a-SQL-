from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Prestamo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    libro_id: int = Field(foreign_key="libro.id")
    cliente_nombre: str = Field(min_length=1)
    fecha_prestamo: datetime = Field(default_factory=datetime.now)
    fecha_devolucion: Optional[datetime] = None
    devuelto: bool = Field(default=False)
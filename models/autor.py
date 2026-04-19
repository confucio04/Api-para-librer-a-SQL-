from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .libro import Libro

class Autor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(min_length=1) 
    nacionalidad: str
    fecha_nacimiento: int

    libros: List["Libro"] = Relationship(back_populates="autor")
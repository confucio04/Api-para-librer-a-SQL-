from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .autor import Autor

class Libro(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str = Field(min_length=1, max_length=200) # 
    isbn: str = Field(min_length=10, max_length=13) # 
    precio: float = Field(gt=0)  
    stock: int = Field(ge=0)  
    
    autor_id: int = Field(foreign_key="autor.id")
    autor: Optional["Autor"] = Relationship(back_populates="libros")
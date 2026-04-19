from fastapi import FastAPI, Depends, HTTPException, Query
from sqlmodel import Session, select, func 
from database import engine, create_db_and_tables, get_session
from models import Autor, Libro, Prestamo  
from datetime import datetime, timedelta 

app = FastAPI(title="Librería El Quijote")

@app.on_event("startup")
def on_startup():
    create_db_and_tables() 

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de la Librería El Quijote"}

@app.post("/autores", response_model=Autor)
def crear_autor(autor: Autor, session: Session = Depends(get_session)):
    session.add(autor) 
    session.commit()   
    session.refresh(autor) 
    return autor

@app.get("/autores")
def listar_autores(session: Session = Depends(get_session)):
    autores = session.exec(select(Autor)).all()
    return autores

# --- CRUD LIBROS ---

@app.post("/libros", response_model=Libro)
def crear_libro(libro: Libro, session: Session = Depends(get_session)):
    autor = session.get(Autor, libro.autor_id)
    if not autor:
        raise HTTPException(status_code=404, detail="El autor especificado no existe")
    
    if not libro.isbn.isdigit():
        raise HTTPException(status_code=400, detail="El ISBN debe contener solo dígitos")
        
    session.add(libro)
    session.commit()
    session.refresh(libro)
    return libro

@app.get("/libros")
def listar_libros(
    titulo: str = Query(None), 
    autor_id: int = Query(None), 
    precio_max: float = Query(None), 
    session: Session = Depends(get_session)
):
    statement = select(Libro)
    if titulo:
        statement = statement.where(Libro.titulo.contains(titulo))
    if autor_id:
        statement = statement.where(Libro.autor_id == autor_id)
    if precio_max:
        statement = statement.where(Libro.precio <= precio_max)
        
    return session.exec(statement).all()


@app.get("/libros/{id}")
def obtener_libro(id: int, session: Session = Depends(get_session)):
    libro = session.get(Libro, id)
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return libro

# --- MÓDULO DE PRÉSTAMOS ---

@app.get("/prestamos")
def listar_prestamos(session: Session = Depends(get_session)):
    return session.exec(select(Prestamo)).all()

@app.get("/prestamos/activos")
def listar_prestamos_activos(session: Session = Depends(get_session)):
    statement = select(Prestamo).where(Prestamo.devuelto == False)
    return session.exec(statement).all()

@app.post("/prestamos", response_model=Prestamo)
def registrar_prestamo(prestamo: Prestamo, session: Session = Depends(get_session)):
  
    libro = session.get(Libro, prestamo.libro_id)
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    
    if libro.stock <= 0:
        raise HTTPException(status_code=400, detail="No hay stock disponible para este libro")
    
    libro.stock -= 1
    session.add(libro)
    
    session.add(prestamo)
    session.commit()
    session.refresh(prestamo)
    return prestamo


@app.patch("/prestamos/{id}/devolver")
def devolver_libro(id: int, session: Session = Depends(get_session)):
    prestamo = session.get(Prestamo, id)
    if not prestamo:
        raise HTTPException(status_code=404, detail="Registro de préstamo no encontrado")
    
    if prestamo.devuelto:
        raise HTTPException(status_code=400, detail="Este préstamo ya fue marcado como devuelto")
    
    libro = session.get(Libro, prestamo.libro_id)
    libro.stock += 1
    
    prestamo.devuelto = True
    prestamo.fecha_devolucion = datetime.now()
    
    session.add(libro)
    session.add(prestamo)
    session.commit()
    return {"message": "Libro devuelto exitosamente y stock actualizado"}
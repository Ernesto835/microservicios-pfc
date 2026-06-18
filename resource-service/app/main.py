from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

# Importaciones locales de tu proyecto
from app import models, schemas
from app.database import engine, get_db

# Crear las tablas en la base de datos SQLite si no existen
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Resource Service - Loans Management",
    description="Microservicio para la gestión estandarizada de préstamos del PROYECTO-PFC",
    version="1.0.0"
)

# Función utilitaria para generar respuestas con el formato de StandardResponse
def json_response(status: str, message: str, data: dict | list | None = None) -> dict:
    return {
        "status": status,
        "data": data,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }

# --- CORRECCIÓN DE ENRUTAMIENTO PERIMETRAL PARA NGINX ---
# Cambiamos la ruta raíz para que responda directo en el prefijo base del Gateway
@app.get("/", response_model=schemas.StandardResponse)
def read_root():
    return json_response(
        status="success",
        message="Resource Service (Loans) operando correctamente",
        data={"service": "resource-service", "status": "UP"}
    )

# --- ENDPOINTS CRUD PARA PRÉSTAMOS (LOANS) ---

@app.post("/loans/", response_model=schemas.StandardResponse, status_code=status.HTTP_201_CREATED)
def create_loan(loan: schemas.LoanCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo préstamo en el sistema.
    """
    db_loan = models.Loan(**loan.model_dump())
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    
    # Convertimos el modelo de la DB a un diccionario compatible con Pydantic
    loan_data = schemas.LoanResponse.model_validate(db_loan).model_dump()
    
    return json_response(
        status="success",
        message="Préstamo registrado exitosamente",
        data=loan_data
    )

@app.get("/loans/", response_model=schemas.StandardResponse)
def read_loans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Obtiene el listado de todos los préstamos registrados.
    """
    loans = db.query(models.Loan).offset(skip).limit(limit).all()
    # Serializamos la lista de objetos SQLAlchemy usando el esquema de respuesta
    loans_list = [schemas.LoanResponse.model_validate(l).model_dump() for l in loans]
    
    return json_response(
        status="success",
        message="Listado de préstamos recuperado con éxito",
        data=loans_list
    )

@app.get("/loans/{loan_id}", response_model=schemas.StandardResponse)
def read_loan(loan_id: int, db: Session = Depends(get_db)):
    """
    Busca un préstamo específico mediante su ID.
    """
    db_loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if db_loan is None:
        raise HTTPException(
            status_code=404, 
            detail=json_response(status="error", message=f"Préstamo con ID {loan_id} no encontrado")
        )
    
    loan_data = schemas.LoanResponse.model_validate(db_loan).model_dump()
    return json_response(
        status="success",
        message="Préstamo encontrado",
        data=loan_data
    )

@app.put("/loans/{loan_id}", response_model=schemas.StandardResponse)
def update_loan(loan_id: int, loan_update: schemas.LoanCreate, db: Session = Depends(get_db)):
    """
    Actualiza por completo la información de un préstamo existente.
    """
    db_loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if db_loan is None:
        raise HTTPException(
            status_code=404, 
            detail=json_response(status="error", message=f"No se pudo actualizar. Préstamo con ID {loan_id} no existe")
        )
    
    # Actualizar dinámicamente los campos
    for key, value in loan_update.model_dump().items():
        setattr(db_loan, key, value)
        
    db.commit()
    db.refresh(db_loan)
    
    loan_data = schemas.LoanResponse.model_validate(db_loan).model_dump()
    return json_response(
        status="success",
        message="Préstamo actualizado correctamente",
        data=loan_data
    )

@app.delete("/loans/{loan_id}", response_model=schemas.StandardResponse)
def delete_loan(loan_id: int, db: Session = Depends(get_db)):
    """
    Elimina un registro de préstamo por su ID.
    """
    db_loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if db_loan is None:
        raise HTTPException(
            status_code=404, 
            detail=json_response(status="error", message=f"No se pudo eliminar. Préstamo con ID {loan_id} no existe")
        )
    
    db.delete(db_loan)
    db.commit()
    
    return json_response(
        status="success",
        message=f"Préstamo con ID {loan_id} eliminado de la base de datos"
    )
from fastapi import FastAPI, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import engine, Base, get_db
from app.models import User
from app.security import get_password_hash, verify_password, create_access_token, decode_access_token
from app.schemas import UserLogin, UserRegister, StandardResponse

# Generar automáticamente la base de datos y sus tablas al arrancar
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Service - PFC UTEQ", version="1.0.0")

# --- ENDPOINTS CORREGIDOS CON FLEXIBILIDAD DE RUTA (CON/SIN BARRA) ---

@app.post("/register", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
@app.post("/register/", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario en la base de datos SQLite distribuida.
    Soporta rutas con y sin barra diagonal para acoplarse a Nginx.
    """
    # 1. Verificar si el usuario ya existe en la base de datos
    db_user = db.query(User).filter(User.username == user_data.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    # 2. Encriptar la contraseña e instanciar el nuevo registro
    hashed = get_password_hash(user_data.password)
    new_user = User(username=user_data.username, hashed_password=hashed)
    
    # 3. Guardar en la base de datos
    db.add(new_user)
    db.commit()
    
    # 4. Retornar formato JSON estándar corregido para evitar fallos de serialización
    return {
        "status": "success",
        "data": {"username": str(user_data.username)},
        "message": "Usuario registrado exitosamente en SQLite",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/login", response_model=StandardResponse)
@app.post("/login/", response_model=StandardResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Autentica al usuario y genera un Token JWT unificado.
    Soporta rutas con y sin barra diagonal para acoplarse a Nginx.
    """
    # 1. Buscar al usuario por su nombre de usuario
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    # 2. Generar el token JWT con expiración de 1 hora (Requisito de la guía)
    access_token = create_access_token(data={"sub": user.username, "user_id": user.id})
    
    # 3. Retornar formato estándar JSON
    return {
        "status": "success",
        "data": {"access_token": access_token, "token_type": "bearer"},
        "message": "Autenticación satisfactoria",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/validate", response_model=StandardResponse)
@app.get("/validate/", response_model=StandardResponse)
def validate_token(authorization: str = Header(None)):
    """
    Intercepta y valida la cabecera HTTP de tokens distribuidos.
    Soporta rutas con y sin barra diagonal para acoplarse a Nginx.
    """
    # 1. Validar que la cabecera de autorización esté presente y sea válida
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Formato de token inválido o ausente")
    
    # 2. Extraer el token de la cadena "Bearer <TOKEN>"
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    
    # 3. Si la decodificación falla (token expirado o alterado), denegar acceso
    if payload is None:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
        
    # 4. Retornar los datos decodificados del usuario
    return {
        "status": "success",
        "data": payload,
        "message": "Token válido",
        "timestamp": datetime.now().isoformat()
    }
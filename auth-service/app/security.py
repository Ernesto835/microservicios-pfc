import os
import hashlib
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

# Variables de entorno con valores seguros por defecto
SECRET_KEY = os.getenv("JWT_SECRET", "super-secret-key-pfc-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Requisito de la guía: Expiración de 1 hora

def get_password_hash(password: str) -> str:
    # Genera un hash seguro usando la librería nativa de Python
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Compara el hash de la clave ingresada con el guardado
    return get_password_hash(plain_password) == hashed_password

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
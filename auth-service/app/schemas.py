from pydantic import BaseModel
from datetime import datetime

class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    password: str

# Requisito obligatorio: Formato de respuesta estandarizado por el docente
class StandardResponse(BaseModel):
    status: str
    data: dict | list | None = None
    message: str
    timestamp: str = datetime.now().isoformat()
from pydantic import BaseModel
from datetime import datetime

class LoanCreate(BaseModel):
    client_name: str
    amount: float
    description: str

class LoanResponse(BaseModel):
    id: int
    client_name: str
    amount: float
    description: str
    created_at: datetime

    class Config:
        from_attributes = True

class StandardResponse(BaseModel):
    status: str
    data: dict | list | None
    message: str
    timestamp: str
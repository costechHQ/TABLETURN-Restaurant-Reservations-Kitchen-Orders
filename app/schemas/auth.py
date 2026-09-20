from datetime import datetime

from pydandic import BaseModel, EmailStr
from app.models.user import userRole


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: userRole = userRole.DINER

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class userResponse(BaseModel):
    id: int
    email: EmailStr
    role: userRole
    created_at: datetime
  

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

    




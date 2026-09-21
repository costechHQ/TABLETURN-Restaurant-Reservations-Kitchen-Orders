from datetime import datetime

from pydantic import BaseModel, EmailStr
from app.models.user import UserRole
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = UserRole.DINER

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    created_at: datetime
class userResponse(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    created_at: datetime
  

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

# Схемы для контактов
class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
    additional_info: Optional[str] = None

class ContactCreate(ContactBase):
    pass

class ContactUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    birthday: Optional[date] = None
    additional_info: Optional[str] = None

class ContactInDB(ContactBase):
    id: int

    class Config:
        orm_mode = True

# Схемы для пользователей
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: int
    is_verified: bool
    avatar_url: Optional[str] = None

    class Config:
        orm_mode = True

# Схемы для токенов
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None

# Схема для верификации email
class EmailVerification(BaseModel):
    email: EmailStr
    token: str

from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: str = Field(default="", max_length=30)
    password: str = Field(min_length=8, max_length=128)

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class ProductIn(BaseModel):
    name: str
    category: str = "Healthcare"
    description: str = ""
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    prescription_required: bool = False
    image_url: str = ""

class OrderItem(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, le=50)

class OrderIn(BaseModel):
    items: list[OrderItem]
    address: str = Field(min_length=10, max_length=1000)
    payment_method: str = "COD"
    prescription_id: Optional[int] = None

class StatusIn(BaseModel):
    status: str

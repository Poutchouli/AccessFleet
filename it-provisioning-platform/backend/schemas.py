from pydantic import BaseModel, EmailStr, Field
from typing import Any
from models import UserRole

class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    role: UserRole

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class FormDefinitionBase(BaseModel):
    name: str
    description: str | None = None
    form_schema: dict[str, Any] = Field(..., alias="schema")  # Use alias to avoid shadowing

class FormDefinitionCreate(FormDefinitionBase):
    pass

class FormDefinition(FormDefinitionBase):
    id: int
    created_by_admin_id: int

    class Config:
        from_attributes = True
        populate_by_name = True

class RequestBase(BaseModel):
    form_definition_id: int
    form_data: dict[str, Any]

class RequestCreate(RequestBase):
    pass

class Request(RequestBase):
    id: int
    status: str
    submitted_by_manager_id: int

    class Config:
        from_attributes = True

from pydantic import BaseModel, EmailStr, Field
from typing import Any
from datetime import datetime
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
    walkthrough_state: dict[str, Any] | None = None
    assigned_temp_account_id: int | None = None

    class Config:
        from_attributes = True

class TempAccountBase(BaseModel):
    user_principal_name: str
    display_name: str
    is_in_use: bool = False

class TempAccountCreate(TempAccountBase):
    pass

class TempAccount(TempAccountBase):
    id: int

    class Config:
        from_attributes = True

class AuditLog(BaseModel):
    id: int
    timestamp: datetime
    actor_id: int
    event_type: str
    details: dict[str, Any]

    class Config:
        from_attributes = True

class WalkthroughTemplateBase(BaseModel):
    name: str
    description: str
    steps: list[dict[str, Any]]

class WalkthroughTemplateCreate(WalkthroughTemplateBase):
    pass

class WalkthroughTemplate(WalkthroughTemplateBase):
    id: int

    class Config:
        from_attributes = True

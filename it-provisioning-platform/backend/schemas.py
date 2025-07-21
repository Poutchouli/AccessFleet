from pydantic import BaseModel, EmailStr, Field
from typing import Any
from datetime import datetime
from models import UserRole

class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    role: UserRole
    service: str | None = None

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

class SharedMailboxBase(BaseModel):
    display_name: str
    primary_smtp_address: str
    full_access_users: str | None = None

class SharedMailboxCreate(SharedMailboxBase):
    pass

class SharedMailbox(SharedMailboxBase):
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

# New User Creation schemas
class NewADUser(BaseModel):
    first_name: str
    last_name: str
    sam_account_name: str  # This is the unique login name
    department: str
    password: str

# Mailbox Modification schemas
class MailboxModification(BaseModel):
    mailbox_id: int
    mailbox_name: str
    add_users: list[str]  # List of user emails to add
    remove_users: list[str]  # List of user emails to remove

class MailboxModificationRequest(BaseModel):
    modifications: list[MailboxModification]

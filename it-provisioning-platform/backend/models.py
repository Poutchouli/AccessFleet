from sqlalchemy import Column, Integer, String, Enum as SQLAlchemyEnum, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from database import Base
import enum

class UserRole(str, enum.Enum):
    manager = "manager"
    admin = "admin"

class RequestStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    rejected = "rejected"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    role = Column(SQLAlchemyEnum(UserRole))

class FormDefinition(Base):
    __tablename__ = "form_definitions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    schema = Column(JSONB)  # Column for the form builder's JSON output
    created_by_admin_id = Column(Integer, ForeignKey("users.id"))

class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(SQLAlchemyEnum(RequestStatus), default=RequestStatus.pending)
    form_data = Column(JSONB)  # Stores the user's answers
    
    submitted_by_manager_id = Column(Integer, ForeignKey("users.id"))
    processed_by_admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    form_definition_id = Column(Integer, ForeignKey("form_definitions.id"))

class TempAccount(Base):
    __tablename__ = "temp_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_principal_name = Column(String, unique=True, index=True)
    display_name = Column(String, index=True)
    is_in_use = Column(Boolean, default=False)  # Track if account is currently assigned

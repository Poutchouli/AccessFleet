from sqlalchemy import (
    Boolean, Column, Integer, String, Enum as SQLAlchemyEnum, 
    ForeignKey, DateTime, Text, Table
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import enum

# Association table for many-to-many relationship between managers and shared mailboxes
manager_mailbox_association = Table(
    "manager_mailbox_association",
    Base.metadata,
    Column("manager_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("mailbox_id", Integer, ForeignKey("shared_mailboxes.id"), primary_key=True),
)

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
    service = Column(String, index=True, nullable=True)  # Department/Service field
    
    # Relationship: managers can see specific shared mailboxes
    visible_mailboxes = relationship(
        "SharedMailbox",
        secondary=manager_mailbox_association,
        back_populates="visible_to_managers"
    )
    
    # Alias for clearer naming in the mailbox management context
    managed_mailboxes = relationship(
        "SharedMailbox",
        secondary=manager_mailbox_association,
        back_populates="managing_managers",
        overlaps="visible_mailboxes"
    )

class FormDefinition(Base):
    __tablename__ = "form_definitions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    schema = Column(JSONB)  # Column for the form builder's JSON output
    created_by_admin_id = Column(Integer, ForeignKey("users.id"))
    suggested_walkthrough_id = Column(Integer, ForeignKey("walkthrough_templates.id"), nullable=True)

class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(SQLAlchemyEnum(RequestStatus), default=RequestStatus.pending)
    form_data = Column(JSONB)  # Stores the user's answers
    walkthrough_state = Column(JSONB, nullable=True)  # To store checklist progress
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    submitted_by_manager_id = Column(Integer, ForeignKey("users.id"))
    processed_by_admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    form_definition_id = Column(Integer, ForeignKey("form_definitions.id"))
    assigned_temp_account_id = Column(Integer, ForeignKey("temp_accounts.id"), nullable=True)

class TempAccount(Base):
    __tablename__ = "temp_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_principal_name = Column(String, unique=True, index=True)
    display_name = Column(String, index=True)
    is_in_use = Column(Boolean, default=False)  # Track if account is currently assigned

class SharedMailbox(Base):
    __tablename__ = "shared_mailboxes"

    id = Column(Integer, primary_key=True, index=True)
    display_name = Column(String, index=True)
    primary_smtp_address = Column(String, unique=True, index=True)
    full_access_users = Column(Text, nullable=True)  # Semicolon-separated list of users
    
    # Relationship: shared mailboxes can be visible to specific managers
    visible_to_managers = relationship(
        "User",
        secondary=manager_mailbox_association,
        back_populates="visible_mailboxes",
        overlaps="managed_mailboxes"
    )
    
    # Alias for clearer naming in the mailbox management context
    managing_managers = relationship(
        "User",
        secondary=manager_mailbox_association,
        back_populates="managed_mailboxes",
        overlaps="visible_mailboxes,visible_to_managers"
    )

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    actor_id = Column(Integer, ForeignKey("users.id"))
    event_type = Column(String, index=True)
    details = Column(JSONB)  # To store flexible event data

class WalkthroughTemplate(Base):
    __tablename__ = "walkthrough_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    steps = Column(JSONB)
    tools = Column(JSONB, nullable=True)  # e.g., ["new_user_form", "temp_account_assignment"]

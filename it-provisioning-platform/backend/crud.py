from sqlalchemy.orm import Session
from sqlalchemy import func, Date
import models, schemas

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(email=user.email, full_name=user.full_name, role=user.role, service=user.service)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_form_definition(db: Session, form: schemas.FormDefinitionCreate, user_id: int):
    db_form = models.FormDefinition(
        name=form.name,
        description=form.description,
        schema=form.form_schema,
        created_by_admin_id=user_id
    )
    db.add(db_form)
    db.commit()
    db.refresh(db_form)
    return db_form

def get_form_definitions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.FormDefinition).offset(skip).limit(limit).all()

def get_form_definition(db: Session, form_id: int):
    return db.query(models.FormDefinition).filter(models.FormDefinition.id == form_id).first()

def create_request(db: Session, request: schemas.RequestCreate, user_id: int):
    db_request = models.Request(
        form_definition_id=request.form_definition_id,
        form_data=request.form_data,
        submitted_by_manager_id=user_id
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request

def get_requests(db: Session, skip: int = 0, limit: int = 100, service: str | None = None):
    query = db.query(models.Request)
    
    if service:
        # Join with the User table and filter by the 'service' column
        query = query.join(models.User, models.Request.submitted_by_manager_id == models.User.id).filter(models.User.service == service)
        
    return query.order_by(models.Request.timestamp.desc()).offset(skip).limit(limit).all()

def get_temp_accounts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.TempAccount).offset(skip).limit(limit).all()

def get_temp_account_by_upn(db: Session, upn: str):
    return db.query(models.TempAccount).filter(models.TempAccount.user_principal_name == upn).first()

def create_temp_account(db: Session, account: schemas.TempAccountCreate):
    db_account = models.TempAccount(
        user_principal_name=account.user_principal_name,
        display_name=account.display_name,
        is_in_use=account.is_in_use
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def create_audit_log(db: Session, *, actor_id: int, event_type: str, details: dict):
    log_entry = models.AuditLog(
        actor_id=actor_id,
        event_type=event_type,
        details=details
    )
    db.add(log_entry)
    db.commit()  # Commit immediately to ensure log is saved
    return log_entry

def get_audit_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.AuditLog).order_by(models.AuditLog.timestamp.desc()).offset(skip).limit(limit).all()

# Walkthrough Template CRUD functions
def create_walkthrough_template(db: Session, template: schemas.WalkthroughTemplateCreate):
    db_template = models.WalkthroughTemplate(
        name=template.name,
        description=template.description,
        steps=template.steps,
        tools=template.tools
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

def get_walkthrough_templates(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.WalkthroughTemplate).offset(skip).limit(limit).all()

def get_walkthrough_template(db: Session, template_id: int):
    return db.query(models.WalkthroughTemplate).filter(models.WalkthroughTemplate.id == template_id).first()

def update_walkthrough_template(db: Session, template_id: int, template: schemas.WalkthroughTemplateUpdate):
    db_template = db.query(models.WalkthroughTemplate).filter(models.WalkthroughTemplate.id == template_id).first()
    if db_template:
        if template.name is not None:
            db_template.name = template.name
        if template.description is not None:
            db_template.description = template.description
        if template.steps is not None:
            db_template.steps = template.steps
        if template.tools is not None:
            db_template.tools = template.tools
        db.commit()
        db.refresh(db_template)
    return db_template

def delete_walkthrough_template(db: Session, template_id: int):
    db_template = db.query(models.WalkthroughTemplate).filter(models.WalkthroughTemplate.id == template_id).first()
    if db_template:
        db.delete(db_template)
        db.commit()
        return True
    return False

# Analytics functions
def get_request_volume_by_day(db: Session, days_limit: int = 30):
    return (
        db.query(
            func.cast(models.Request.timestamp, Date).label("date"),
            func.count(models.Request.id).label("count")
        )
        .group_by(func.cast(models.Request.timestamp, Date))
        .order_by(func.cast(models.Request.timestamp, Date).desc())
        .limit(days_limit)
        .all()
    )

def get_request_status_breakdown(db: Session):
    return (
        db.query(
            models.Request.status.label("status"),
            func.count(models.Request.id).label("count")
        )
        .group_by(models.Request.status)
        .all()
    )

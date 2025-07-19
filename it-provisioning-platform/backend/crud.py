from sqlalchemy.orm import Session
import models, schemas

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(email=user.email, full_name=user.full_name, role=user.role)
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

def get_requests(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Request).offset(skip).limit(limit).all()

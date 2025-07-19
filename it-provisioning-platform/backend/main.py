from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import models, schemas, crud
from database import engine, get_db

# This creates the tables. If they already exist, it does nothing.
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.post("/form-definitions/", response_model=schemas.FormDefinition)
def create_form_definition(form: schemas.FormDefinitionCreate, db: Session = Depends(get_db)):
    # In a real app, you'd get the user_id from an authenticated token.
    # For now, we'll hardcode it to the first admin user.
    admin_user = db.query(models.User).filter(models.User.role == models.UserRole.admin).first()
    if not admin_user:
        raise HTTPException(status_code=404, detail="No admin user found to assign form to.")
    
    try:
        # Cast to int to satisfy type checker - at runtime this will be an int
        user_id: int = admin_user.id  # type: ignore
        return crud.create_form_definition(db=db, form=form, user_id=user_id)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Form with this name already exists")

@app.get("/form-definitions/", response_model=list[schemas.FormDefinition])
def read_form_definitions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    forms = crud.get_form_definitions(db, skip=skip, limit=limit)
    return forms

@app.get("/form-definitions/{form_id}", response_model=schemas.FormDefinition)
def read_form_definition(form_id: int, db: Session = Depends(get_db)):
    form = crud.get_form_definition(db, form_id)
    if form is None:
        raise HTTPException(status_code=404, detail="Form definition not found")
    return form

@app.post("/requests/", response_model=schemas.Request)
def create_request(request: schemas.RequestCreate, db: Session = Depends(get_db)):
    # In a real app, you'd get the user_id from an authenticated token.
    # For now, we'll hardcode it to the first manager user.
    manager_user = db.query(models.User).filter(models.User.role == models.UserRole.manager).first()
    if not manager_user:
        raise HTTPException(status_code=404, detail="No manager user found to submit request.")
    user_id: int = manager_user.id  # type: ignore
    return crud.create_request(db=db, request=request, user_id=user_id)

@app.get("/requests/", response_model=list[schemas.Request])
def read_requests(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    requests = crud.get_requests(db, skip=skip, limit=limit)
    return requests
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import models, schemas, crud
from database import engine, get_db
from ws_manager import manager
from models import RequestStatus
import csv
import io

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

# WebSocket endpoint for admin dashboard
@app.websocket("/ws/admin-dashboard")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # We don't need to receive data, just keep the connection open
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

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
async def create_request(request: schemas.RequestCreate, db: Session = Depends(get_db)):
    # In a real app, you'd get the user_id from an authenticated token.
    # For now, we'll hardcode it to the first manager user.
    manager_user = db.query(models.User).filter(models.User.role == models.UserRole.manager).first()
    if not manager_user:
        raise HTTPException(status_code=404, detail="No manager user found to submit request.")
    user_id: int = manager_user.id  # type: ignore
    
    db_request = crud.create_request(db=db, request=request, user_id=user_id)
    
    # Broadcast the new request to all connected admins
    await manager.broadcast({
        "type": "new_request",
        "data": {
            "id": db_request.id,
            "status": db_request.status.value,
            "submitted_by_manager_id": db_request.submitted_by_manager_id,
            "form_definition_id": db_request.form_definition_id,
            "form_data": db_request.form_data
        }
    })
    
    return db_request

@app.get("/requests/", response_model=list[schemas.Request])
def read_requests(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    requests = crud.get_requests(db, skip=skip, limit=limit)
    return requests

# Add the status update endpoint
@app.put("/requests/{request_id}/status", response_model=schemas.Request)
async def update_request_status(
    request_id: int, 
    status: RequestStatus, 
    db: Session = Depends(get_db)
):
    db_request = db.query(models.Request).filter(models.Request.id == request_id).first()
    if not db_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Update the status
    db_request.status = status  # type: ignore
    db.commit()
    db.refresh(db_request)

    # Broadcast the status update
    await manager.broadcast({
        "type": "status_update",
        "data": {"id": request_id, "status": status.value}
    })

    return db_request

# TEMP Accounts endpoints
@app.get("/admin/temp-accounts", response_model=list[schemas.TempAccount])
def get_temp_accounts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    accounts = crud.get_temp_accounts(db, skip=skip, limit=limit)
    return accounts

@app.post("/admin/upload-temp-accounts-csv")
async def upload_temp_accounts_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename or not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV.")

    try:
        # Read CSV content
        contents = await file.read()
        # Decode and read as a file-like object
        stream = io.StringIO(contents.decode("utf-8"))
        reader = csv.DictReader(stream)

        synced_count = 0
        updated_count = 0

        for row in reader:
            # Assumes CSV has 'displayName' and 'userPrincipalName' headers
            upn = row.get("userPrincipalName")
            display_name = row.get("displayName")

            if not upn or not display_name:
                continue

            # Basic upsert logic
            account = crud.get_temp_account_by_upn(db, upn)
            if account:
                # Update existing account if needed
                setattr(account, 'display_name', display_name)
                updated_count += 1
            else:
                # Create new account
                account_data = schemas.TempAccountCreate(
                    user_principal_name=upn,
                    display_name=display_name
                )
                crud.create_temp_account(db, account_data)
                synced_count += 1
        
        db.commit()
        return {"message": f"Sync complete. Added: {synced_count}, Updated: {updated_count}."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {e}")

@app.put("/admin/temp-accounts/{account_id}/status", response_model=dict)
def update_temp_account_status(
    account_id: int, 
    is_in_use: bool, 
    db: Session = Depends(get_db)
):
    account = db.query(models.TempAccount).filter(models.TempAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Update our local database
    setattr(account, 'is_in_use', is_in_use)
    db.commit()
    db.refresh(account)

    # Generate the corresponding PowerShell command
    # NOTE: We assume 'disabling' an account is how we mark it "in use"
    # and 'enabling' it makes it "available".
    ps_enabled_status = "$false" if is_in_use else "$true"
    description = f"'In Use by system'" if is_in_use else "'Available'"
    
    command = (
        f"Set-ADUser -Identity '{account.user_principal_name}' "
        f"-Enabled {ps_enabled_status} "
        f"-Description {description}"
    )

    # Convert the updated account to a dict for the response
    updated_account_data = {
        "id": account.id,
        "user_principal_name": account.user_principal_name,
        "display_name": account.display_name,
        "is_in_use": account.is_in_use
    }

    return {
        "message": "Database updated successfully.",
        "powershell_command": command,
        "updated_account": updated_account_data
    }
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from typing import Any
import models, schemas, crud, auth
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
    allow_origins=["http://localhost:5173", "http://localhost:5174"],  # Frontend URLs
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
def read_requests(
    user: models.User | None = Depends(auth.get_optional_user), # Use auth to get the current user
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    service_filter: str | None = None
    # If the user is a manager, filter by their service
    if user and user.role.value == 'manager':
        # Get the service value properly
        user_service = getattr(user, 'service', None)
        if user_service is not None:
            service_filter = str(user_service)
        
    # If the user is an admin or unlogged, service_filter remains None, so they see all requests
    
    requests = crud.get_requests(db, skip=skip, limit=limit, service=service_filter)
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
    
    # Store original status for audit log
    original_status = db_request.status.value
    
    # Update the status
    db_request.status = status  # type: ignore
    db.commit()
    db.refresh(db_request)

    # Create audit log entry
    admin_user = db.query(models.User).filter(models.User.role == models.UserRole.admin).first()
    if admin_user:
        actor_id = admin_user.id  # Get the actual value
        crud.create_audit_log(
            db=db,
            actor_id=actor_id,  # type: ignore
            event_type="REQUEST_STATUS_CHANGED",
            details={
                "request_id": request_id,
                "from_status": original_status,
                "to_status": status.value
            }
        )

    # Broadcast the status update
    await manager.broadcast({
        "type": "status_update",
        "data": {"id": request_id, "status": status.value}
    })

    return db_request

# Get a specific request by ID
@app.get("/requests/{request_id}", response_model=schemas.Request)
def read_request(request_id: int, db: Session = Depends(get_db)):
    db_request = db.query(models.Request).filter(models.Request.id == request_id).first()
    if db_request is None:
        raise HTTPException(status_code=404, detail="Request not found")
    return db_request

# Schema for walkthrough state updates
class WalkthroughStateUpdate(BaseModel):
    state: dict[str, Any]

# Update walkthrough state for a request
@app.put("/requests/{request_id}/walkthrough-state", response_model=schemas.Request)
def update_walkthrough_state(
    request_id: int, 
    update: WalkthroughStateUpdate, 
    db: Session = Depends(get_db)
):
    db_request = db.query(models.Request).filter(models.Request.id == request_id).first()
    if db_request is None:
        raise HTTPException(status_code=404, detail="Request not found")
    
    db_request.walkthrough_state = update.state  # type: ignore
    db.commit()
    db.refresh(db_request)
    return db_request

# Schema for temp account assignment
class TempAccountAssign(BaseModel):
    temp_account_id: int

# Assign temp account to a request
@app.post("/requests/{request_id}/assign-temp-account", response_model=schemas.Request)
def assign_temp_account(
    request_id: int,
    assignment: TempAccountAssign,
    db: Session = Depends(get_db)
):
    # Get the request
    db_request = db.query(models.Request).filter(models.Request.id == request_id).first()
    if not db_request:
        raise HTTPException(status_code=404, detail="Request not found")

    # Get the temp account and ensure it's available
    db_temp_account = db.query(models.TempAccount).filter(models.TempAccount.id == assignment.temp_account_id).first()
    if not db_temp_account:
        raise HTTPException(status_code=404, detail="Temp account not found")
    if db_temp_account.is_in_use:  # type: ignore
        raise HTTPException(status_code=400, detail="Temp account is already in use")

    # Perform the assignment
    db_temp_account.is_in_use = True  # type: ignore
    db_request.assigned_temp_account_id = db_temp_account.id  # type: ignore
    
    # Log this as an audit event
    admin_user = db.query(models.User).filter(models.User.role == models.UserRole.admin).first()
    if admin_user:
        crud.create_audit_log(
            db=db,
            actor_id=admin_user.id,  # type: ignore
            event_type="TEMP_ACCOUNT_ASSIGNED",
            details={
                "request_id": request_id, 
                "temp_account_id": db_temp_account.id,
                "account_upn": db_temp_account.user_principal_name
            }
        )

    db.commit()
    db.refresh(db_request)
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

    # Store original state for audit log
    original_status = account.is_in_use

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

    # Create audit log entry
    # In a real app, actor_id would come from an authenticated session.
    # We'll hardcode to the first admin for now.
    admin_user = db.query(models.User).filter(models.User.role == models.UserRole.admin).first()
    if admin_user:
        actor_id = admin_user.id  # Get the actual value
        crud.create_audit_log(
            db=db,
            actor_id=actor_id,  # type: ignore
            event_type="TEMP_ACCOUNT_STATUS_CHANGED",
            details={
                "account_id": account_id,
                "user_principal_name": account.user_principal_name,
                "from_status": "available" if not bool(original_status) else "in_use",
                "to_status": "in_use" if is_in_use else "available",
                "powershell_command": command
            }
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

# Audit Log API endpoint
@app.get("/admin/audit-log", response_model=list[schemas.AuditLog])
def read_audit_log(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logs = crud.get_audit_logs(db, skip=skip, limit=limit)
    return logs

# Walkthrough Template endpoints
@app.post("/admin/walkthrough-templates", response_model=schemas.WalkthroughTemplate)
def create_walkthrough_template(
    template: schemas.WalkthroughTemplateCreate,
    db: Session = Depends(get_db)
):
    return crud.create_walkthrough_template(db=db, template=template)

@app.get("/admin/walkthrough-templates", response_model=list[schemas.WalkthroughTemplate])
def read_walkthrough_templates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    templates = crud.get_walkthrough_templates(db, skip=skip, limit=limit)
    return templates

@app.get("/admin/walkthrough-templates/{template_id}", response_model=schemas.WalkthroughTemplate)
def read_walkthrough_template(template_id: int, db: Session = Depends(get_db)):
    template = crud.get_walkthrough_template(db, template_id=template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Walkthrough template not found")
    return template

@app.put("/admin/walkthrough-templates/{template_id}", response_model=schemas.WalkthroughTemplate)
def update_walkthrough_template(
    template_id: int,
    template: schemas.WalkthroughTemplateUpdate,
    db: Session = Depends(get_db)
):
    updated_template = crud.update_walkthrough_template(db=db, template_id=template_id, template=template)
    if updated_template is None:
        raise HTTPException(status_code=404, detail="Walkthrough template not found")
    return updated_template

@app.delete("/admin/walkthrough-templates/{template_id}")
def delete_walkthrough_template(template_id: int, db: Session = Depends(get_db)):
    success = crud.delete_walkthrough_template(db=db, template_id=template_id)
    if not success:
        raise HTTPException(status_code=404, detail="Walkthrough template not found")
    return {"message": "Walkthrough template deleted successfully"}

# Analytics endpoints
@app.get("/analytics/request-volume")
def get_request_volume(db: Session = Depends(get_db)):
    volume_data = crud.get_request_volume_by_day(db)
    # The query result is a list of Row objects, convert them to dicts
    return [{"date": str(row.date), "count": row.count} for row in volume_data]

@app.get("/analytics/status-breakdown")
def get_status_breakdown(db: Session = Depends(get_db)):
    status_data = crud.get_request_status_breakdown(db)
    return [{"status": str(row.status), "count": row.count} for row in status_data]

# New User Creation endpoint
@app.post("/admin/generate-new-user-command", response_model=dict)
def generate_new_user_command(user_data: schemas.NewADUser):
    # Construct the user principal name and full name
    upn = f"{user_data.sam_account_name}@yourdomain.com"  # Replace with your actual domain
    full_name = f"{user_data.first_name} {user_data.last_name}"

    # Generate the PowerShell command
    # This command creates a new user and sets their password, which must be changed on first logon.
    command = (
        f"$password = ConvertTo-SecureString '{user_data.password}' -AsPlainText -Force; "
        f"New-ADUser -Name '{full_name}' "
        f"-GivenName '{user_data.first_name}' "
        f"-Surname '{user_data.last_name}' "
        f"-SamAccountName '{user_data.sam_account_name}' "
        f"-UserPrincipalName '{upn}' "
        f"-Department '{user_data.department}' "
        f"-Path 'OU=Users,DC=yourdomain,DC=com' "  # Specify the OU to create the user in
        f"-AccountPassword $password "
        f"-Enabled $true "
        f"-ChangePasswordAtLogon $true"
    )
    
    return {"powershell_command": command}

@app.post("/admin/upload-ad-users-csv")
async def upload_ad_users_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload and process AD Users CSV to populate the users table.
    Expected CSV columns: DisplayName, EmailAddress
    """
    contents = await file.read()
    stream = io.StringIO(contents.decode("utf-8"))
    reader = csv.DictReader(stream)
    
    new_count = 0
    for row in reader:
        email = row.get("EmailAddress")
        display_name = row.get("DisplayName")
        
        # Skip rows without required fields
        if not email or not display_name:
            continue
            
        # Check if user already exists
        user = crud.get_user_by_email(db, email=email)
        if not user:
            # Create a user with a default role
            user_schema = schemas.UserCreate(
                full_name=display_name,
                email=email,
                role=models.UserRole.manager  # Assign a default role
            )
            crud.create_user(db=db, user=user_schema)
            new_count += 1

    return {"message": f"Processed AD Users. Added {new_count} new users."}

@app.post("/admin/upload-shared-mailboxes-csv")
async def upload_shared_mailboxes_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload and process Shared Mailboxes CSV to populate the shared_mailboxes table.
    Expected CSV columns: DisplayName, PrimarySmtpAddress, FullAccess
    """
    contents = await file.read()
    stream = io.StringIO(contents.decode("utf-8"))
    reader = csv.DictReader(stream)
    
    new_count = 0
    for row in reader:
        primary_smtp = row.get("PrimarySmtpAddress")
        display_name = row.get("DisplayName")
        
        # Skip rows without required fields
        if not primary_smtp or not display_name:
            continue
            
        # Basic upsert logic for shared mailboxes
        mailbox = db.query(models.SharedMailbox).filter_by(primary_smtp_address=primary_smtp).first()
        if not mailbox:
            db_mailbox = models.SharedMailbox(
                display_name=display_name,
                primary_smtp_address=primary_smtp,
                full_access_users=row.get("FullAccess", "")
            )
            db.add(db_mailbox)
            new_count += 1
    db.commit()
    return {"message": f"Processed Shared Mailboxes. Added {new_count} new mailboxes."}

# Endpoint to view shared mailboxes
@app.get("/shared-mailboxes", response_model=list[schemas.SharedMailbox])
def read_shared_mailboxes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    mailboxes = db.query(models.SharedMailbox).offset(skip).limit(limit).all()
    return mailboxes

# =======================
# AUTHENTICATION & RBAC ENDPOINTS
# =======================

# Simple endpoint to get user by ID for frontend authentication
@app.get("/users/{user_id}", response_model=schemas.User)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    """Get user details by ID for session management."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Get shared mailboxes visible to current manager
@app.get("/manager/shared-mailboxes", response_model=list[schemas.SharedMailbox])
def get_manager_mailboxes(current_user: models.User = Depends(auth.require_manager), db: Session = Depends(get_db)):
    """Get shared mailboxes that the current manager is allowed to see."""
    # If manager has no specific permissions, return empty list
    return current_user.visible_mailboxes

# Admin endpoint to grant mailbox visibility to manager
@app.post("/admin/permissions/mailbox-to-manager")
def grant_mailbox_visibility(
    manager_id: int, 
    mailbox_id: int, 
    current_admin: models.User = Depends(auth.require_admin),
    db: Session = Depends(get_db)
):
    """Allow an admin to grant a manager visibility to a specific shared mailbox."""
    manager = db.query(models.User).filter(models.User.id == manager_id).first()
    mailbox = db.query(models.SharedMailbox).filter(models.SharedMailbox.id == mailbox_id).first()

    if not manager or not mailbox:
        raise HTTPException(status_code=404, detail="Manager or Mailbox not found")
    if manager.role.value != 'manager':
        raise HTTPException(status_code=400, detail="User is not a manager")

    # Check if permission already exists
    if mailbox in manager.visible_mailboxes:
        raise HTTPException(status_code=400, detail="Manager already has access to this mailbox")

    manager.visible_mailboxes.append(mailbox)
    db.commit()
    return {"message": f"Manager {manager.full_name} can now see mailbox {mailbox.display_name}"}

# Admin endpoint to revoke mailbox visibility from manager
@app.delete("/admin/permissions/mailbox-to-manager")
def revoke_mailbox_visibility(
    manager_id: int, 
    mailbox_id: int, 
    current_admin: models.User = Depends(auth.require_admin),
    db: Session = Depends(get_db)
):
    """Allow an admin to revoke a manager's visibility to a specific shared mailbox."""
    manager = db.query(models.User).filter(models.User.id == manager_id).first()
    mailbox = db.query(models.SharedMailbox).filter(models.SharedMailbox.id == mailbox_id).first()

    if not manager or not mailbox:
        raise HTTPException(status_code=404, detail="Manager or Mailbox not found")

    # Check if permission exists
    if mailbox not in manager.visible_mailboxes:
        raise HTTPException(status_code=400, detail="Manager does not have access to this mailbox")

    manager.visible_mailboxes.remove(mailbox)
    db.commit()
    return {"message": f"Manager {manager.full_name} can no longer see mailbox {mailbox.display_name}"}

# Get all manager-mailbox permissions (for admin interface)
@app.get("/admin/permissions/manager-mailboxes")
def get_all_manager_permissions(
    current_admin: models.User = Depends(auth.require_admin),
    db: Session = Depends(get_db)
):
    """Get all manager-mailbox permission mappings for admin interface."""
    managers = db.query(models.User).filter(models.User.role == models.UserRole.manager).all()
    permissions = []
    for manager in managers:
        permissions.append({
            "manager_id": manager.id,
            "manager_name": manager.full_name,
            "visible_mailboxes": [
                {
                    "id": mailbox.id,
                    "display_name": mailbox.display_name,
                    "primary_smtp_address": mailbox.primary_smtp_address
                }
                for mailbox in manager.visible_mailboxes
            ]
        })
    return permissions

# Manager endpoint to get their assigned mailboxes for management
@app.get("/manager/mailboxes", response_model=list[schemas.SharedMailbox])
def get_manager_assigned_mailboxes(
    current_manager: models.User = Depends(auth.require_manager),
    db: Session = Depends(get_db)
):
    """Get all mailboxes that the current manager can manage."""
    return current_manager.managed_mailboxes

# Manager endpoint to create mailbox modification request
@app.post("/requests/mailbox-modifications", response_model=schemas.Request)
async def create_mailbox_modification_request(
    request_data: schemas.MailboxModificationRequest,
    current_manager: models.User = Depends(auth.require_manager),
    db: Session = Depends(get_db)
):
    """Allow a manager to submit a batch of mailbox modifications as a request."""
    
    # Validate that all mailboxes belong to this manager
    for modification in request_data.modifications:
        mailbox = db.query(models.SharedMailbox).filter(
            models.SharedMailbox.id == modification.mailbox_id
        ).first()
        
        if not mailbox:
            raise HTTPException(
                status_code=404, 
                detail=f"Mailbox with ID {modification.mailbox_id} not found"
            )
        
        if mailbox not in current_manager.managed_mailboxes:
            raise HTTPException(
                status_code=403, 
                detail=f"You do not have permission to manage mailbox {mailbox.display_name}"
            )
    
    # Create a new request with special mailbox modification form_data
    db_request = models.Request(
        submitted_by_manager_id=current_manager.id,
        form_data={
            "type": "mailbox_modifications",
            "modifications": request_data.model_dump()["modifications"]
        },
        status=models.RequestStatus.pending,
        form_definition_id=1  # We'll use a default form_definition_id for mailbox modifications
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    
    # Broadcast the new request to admins
    await manager.broadcast({
        "type": "new_request",
        "data": {
            "id": db_request.id,
            "status": db_request.status.value,
            "timestamp": db_request.timestamp.isoformat(),
            "submitted_by_manager_id": db_request.submitted_by_manager_id,
            "form_data": db_request.form_data,
            "type": "mailbox_modifications"
        }
    })
    
    return db_request
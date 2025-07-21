from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
import models, database

def get_current_user(
    user_id: int | None = Header(None, alias="user-id"), 
    db: Session = Depends(database.get_db)
) -> models.User | None:
    """Get current user from user_id header. Returns None for unlogged users."""
    if user_id is None:
        return None  # Unlogged user
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user ID")
    return user

def require_admin(user: models.User = Depends(get_current_user)):
    """Require user to be an admin. Raises 403 if not."""
    if not user or user.role.value != 'admin':
        raise HTTPException(status_code=403, detail="Administrator access required")
    return user

def require_manager(user: models.User = Depends(get_current_user)):
    """Require user to be a manager. Raises 403 if not."""
    if not user or user.role.value != 'manager':
        raise HTTPException(status_code=403, detail="Manager access required")
    return user

def require_manager_or_admin(user: models.User = Depends(get_current_user)):
    """Require user to be either a manager or admin. Raises 403 if not."""
    if not user or user.role.value not in ['manager', 'admin']:
        raise HTTPException(status_code=403, detail="Manager or Administrator access required")
    return user

def get_optional_user(user: models.User | None = Depends(get_current_user)) -> models.User | None:
    """Get user if authenticated, otherwise return None. No errors for unlogged users."""
    return user

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer

from app.api import deps
from app.models.user import User
from app.schemas.user import LoginRequest
from app.schemas.token import TokenResponse
from app.services.auth_service import auth_service
from app.schemas.response import APIResponse
from app.schemas.common import ActionResponse

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/login", response_model=APIResponse[TokenResponse])
def login(user_in: LoginRequest, db: Session = Depends(deps.get_db)):
    token = auth_service.login(db=db, username=user_in.username, password=user_in.password)
    return APIResponse(data=token)

@router.post("/logout", response_model=APIResponse[ActionResponse])
def logout(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(deps.get_db)
):
    auth_service.logout(db=db, token=token)
    return APIResponse(data=ActionResponse(msg="Logged out successfully"))

@router.post("/refresh", response_model=APIResponse[TokenResponse])
def refresh_token(
    current_user: User = Depends(deps.get_current_user)
):
    token = auth_service.refresh_token(current_user=current_user)
    return APIResponse(data=token)
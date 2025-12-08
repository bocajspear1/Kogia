
from fastapi import APIRouter, Request, HTTPException

from .types import DataResponse, OptionalStrParam

from typing import List, Any, Union

from pydantic import BaseModel

router = APIRouter(tags=['authentication'])

from backend.auth import ROLES

class AuthenticateResponse(DataResponse):
    api_key: str
    roles: List[str]

class UsernamePassword(BaseModel):
    username: str
    password: str

@router.post('/password')
def version(req : Request, auth_data : UsernamePassword) -> AuthenticateResponse:
    username = auth_data.username
    password = auth_data.password
    if req.app._auth is None:
        raise HTTPException(400, detail="Authentication is not enabled") 
    if username is None and password is None:
        raise HTTPException(400, detail="Invalid authentication request") 
    
    ok, token, roles = req.app._auth.authenticate_new(username.strip(), password.strip())

    if not ok:
        raise HTTPException(401, detail=f"Unauthorized: {token}")

    if "admin" in roles:
        roles += ROLES

    auth_resp = AuthenticateResponse(api_key=token, roles=roles)
    return auth_resp
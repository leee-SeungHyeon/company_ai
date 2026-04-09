from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from config import API_KEYS

bearer = HTTPBearer()


def get_user_roles(credentials: HTTPAuthorizationCredentials = Depends(bearer)) -> list[str]:
    roles = API_KEYS.get(credentials.credentials)
    if roles is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return roles

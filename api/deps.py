from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from services import tokens

_bearer = HTTPBearer(auto_error=False)


def get_current_user_id(credentials: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> str:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Falta el header Authorization: Bearer <token>")
    try:
        return tokens.read_session_token(credentials.credentials)
    except ValueError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e)) from e

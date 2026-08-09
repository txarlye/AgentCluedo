from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

from config import settings
from services import credit_ledger, tokens

router = APIRouter(prefix="/v1/auth", tags=["auth"])


class RequestLinkBody(BaseModel):
    email: EmailStr


class RequestLinkResponse(BaseModel):
    sent: bool
    dev_token: str | None = None


class VerifyResponse(BaseModel):
    session_token: str
    user_id: str
    credits_balance: int


@router.post("/request-link", response_model=RequestLinkResponse)
def request_link(body: RequestLinkBody) -> RequestLinkResponse:
    link_token = tokens.create_link_token(body.email)

    if settings.auth_dev_mode:
        # Modo dev: devolvemos el token directamente, sin enviar email de verdad.
        return RequestLinkResponse(sent=False, dev_token=link_token)

    raise HTTPException(
        status.HTTP_501_NOT_IMPLEMENTED,
        "Envío real de email no implementado todavía. Usa AUTH_DEV_MODE=true.",
    )


@router.get("/verify", response_model=VerifyResponse)
def verify(token: str) -> VerifyResponse:
    try:
        email = tokens.read_link_token(token)
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e)) from e

    # El email hace de user_id: es único, y nos ahorra un índice secundario
    # para buscar usuarios por email en esta primera versión.
    user = credit_ledger.get_or_create_user(user_id=email, email=email)
    session_token = tokens.create_session_token(user_id=email)

    return VerifyResponse(
        session_token=session_token,
        user_id=email,
        credits_balance=int(user["credits_balance"]),
    )

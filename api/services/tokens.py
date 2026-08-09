from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from config import settings

_link_serializer = URLSafeTimedSerializer(settings.auth_token_secret, salt="magic-link")
_session_serializer = URLSafeTimedSerializer(settings.auth_token_secret, salt="session")


def create_link_token(email: str) -> str:
    return _link_serializer.dumps({"email": email})


def read_link_token(token: str) -> str:
    """Devuelve el email si el token es válido; lanza ValueError si no."""
    try:
        data = _link_serializer.loads(token, max_age=settings.auth_link_token_max_age_seconds)
    except (BadSignature, SignatureExpired) as e:
        raise ValueError("Enlace inválido o caducado") from e
    return data["email"]


def create_session_token(user_id: str) -> str:
    return _session_serializer.dumps({"user_id": user_id})


def read_session_token(token: str) -> str:
    """Devuelve el user_id si el token es válido; lanza ValueError si no."""
    try:
        data = _session_serializer.loads(token, max_age=settings.auth_session_token_max_age_seconds)
    except (BadSignature, SignatureExpired) as e:
        raise ValueError("Sesión inválida o caducada") from e
    return data["user_id"]

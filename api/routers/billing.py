import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from config import settings
from deps import get_current_user_id
from services import credit_ledger, idempotency

router = APIRouter(prefix="/v1/billing", tags=["billing"])


class CheckoutSessionResponse(BaseModel):
    checkout_url: str


class CreditsResponse(BaseModel):
    credits_balance: int


class DevGrantBody(BaseModel):
    credits: int = 5


@router.post("/checkout-session", response_model=CheckoutSessionResponse)
def create_checkout_session(user_id: str = Depends(get_current_user_id)) -> CheckoutSessionResponse:
    if not settings.stripe_secret_key or not settings.stripe_price_id:
        raise HTTPException(
            status.HTTP_501_NOT_IMPLEMENTED,
            "Stripe no está configurado todavía en este entorno. "
            "Usa POST /v1/billing/dev-grant-credits mientras tanto (solo con AUTH_DEV_MODE=true).",
        )

    stripe.api_key = settings.stripe_secret_key
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{"price": settings.stripe_price_id, "quantity": 1}],
        success_url="http://localhost:8090/static/demo.html?checkout=success",
        cancel_url="http://localhost:8090/static/demo.html?checkout=cancel",
        client_reference_id=user_id,
        metadata={"user_id": user_id, "credits": settings.stripe_price_credits},
    )
    return CheckoutSessionResponse(checkout_url=session.url)


@router.post("/webhook")
async def stripe_webhook(request: Request):
    # Body crudo, sin parseo pydantic: la verificación de firma de Stripe
    # necesita los bytes exactos que Stripe envió.
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    if not settings.stripe_webhook_secret:
        raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Stripe webhook no configurado todavía.")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Webhook inválido: {e}") from e

    if event["type"] == "checkout.session.completed":
        if idempotency.mark_event_processed(event["id"]):
            session = event["data"]["object"]
            user_id = session["client_reference_id"]
            credits = int(session["metadata"]["credits"])
            credit_ledger.grant_credits(user_id, credits)

    return {"received": True}


@router.get("/credits", response_model=CreditsResponse)
def get_credits(user_id: str = Depends(get_current_user_id)) -> CreditsResponse:
    return CreditsResponse(credits_balance=credit_ledger.get_credits(user_id))


@router.post("/dev-grant-credits", response_model=CreditsResponse)
def dev_grant_credits(body: DevGrantBody, user_id: str = Depends(get_current_user_id)) -> CreditsResponse:
    if not settings.auth_dev_mode:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Solo disponible con AUTH_DEV_MODE=true.")
    balance = credit_ledger.grant_credits(user_id, body.credits)
    return CreditsResponse(credits_balance=balance)

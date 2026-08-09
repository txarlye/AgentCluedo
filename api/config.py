from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # AWS / DynamoDB
    aws_region: str = "us-east-1"
    # En local apunta a DynamoDB Local (docker-compose.yml). En AWS real se
    # deja vacío para que boto3 use el endpoint real del servicio.
    dynamodb_endpoint_url: str | None = "http://localhost:8500"
    games_table: str = "agentcluedo_games"
    users_table: str = "agentcluedo_users"
    stripe_events_table: str = "agentcluedo_stripe_events"

    # LLM (motor cluedo_engine) — Ollama por defecto mientras no se añade
    # la rama Bedrock (paso 7 del roadmap, deliberadamente pospuesto)
    llm_provider: str = "ollama"
    ollama_model: str = "llama3.1:8b"
    openai_api_key: str | None = None

    # Auth (magic-link)
    auth_dev_mode: bool = True
    auth_token_secret: str = "dev-secret-cambia-esto-en-produccion"
    auth_link_token_max_age_seconds: int = 900
    auth_session_token_max_age_seconds: int = 60 * 60 * 24 * 7

    # Stripe (modo test). Mientras no haya claves reales, el endpoint de
    # checkout devuelve 501 y la demo usa /v1/billing/dev-grant-credits.
    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None
    stripe_price_id: str | None = None
    stripe_price_credits: int = 5


settings = Settings()

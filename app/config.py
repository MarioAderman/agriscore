from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://agriscore:agriscore@localhost:5432/agriscore"

    # LLM provider selection
    # "bedrock" = Claude via AWS Bedrock (IAM auth, no API key needed on AWS)
    # "anthropic" = Claude via direct API (needs ANTHROPIC_API_KEY)
    # "openai" / "groq" = OpenAI-compatible providers
    llm_provider: str = "bedrock"  # "bedrock" | "anthropic" | "openai" | "groq"
    llm_model: str = ""  # empty = use provider default

    # Anthropic
    anthropic_api_key: str = ""

    # OpenAI (agent + Whisper STT + TTS)
    openai_api_key: str = ""

    # Groq (fast inference, OpenAI-compatible)
    groq_api_key: str = ""

    # Sentinel Hub (Copernicus Data Space)
    sentinel_hub_id: str = ""
    sentinel_hub_secret: str = ""

    # INEGI
    inegi_token: str = ""

    # EvolutionAPI
    evolutionapi_url: str = "http://localhost:8080"
    evolutionapi_authentication_api_key: str = ""
    evolution_instance_name: str = "Fintegra solutions"

    # AWS
    aws_default_region: str = "us-east-1"
    s3_bucket: str = "agriscore-data"
    step_functions_arn: str = ""

    # Cognito
    cognito_user_pool_id: str = ""
    cognito_app_client_id: str = ""

    # SageMaker
    sagemaker_endpoint: str = ""

    # App
    environment: str = "development"
    log_level: str = "INFO"
    customer_api_key: str = "demo-customer-key"
    # CORS: comma-separated allowed origins (use "*" only in development)
    allowed_origins: str = "*"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

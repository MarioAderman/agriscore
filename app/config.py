from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://agriscore:agriscore@localhost:5432/agriscore"

    # Anthropic
    anthropic_api_key: str = ""

    # OpenAI (Whisper STT + TTS)
    openai_api_key: str = ""

    # Sentinel Hub (Copernicus Data Space)
    sentinel_hub_id: str = ""
    sentinel_hub_secret: str = ""

    # INEGI
    inegi_token: str = ""

    # EvolutionAPI
    evolution_api_url: str = "http://localhost:8080"
    evolution_api_key: str = ""
    evolution_instance_name: str = "agriscore"

    # AWS
    aws_default_region: str = "us-east-1"
    s3_bucket: str = "agriscore-data"
    step_functions_arn: str = ""

    # App
    environment: str = "development"
    log_level: str = "INFO"
    bank_api_key: str = "demo-bank-key"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/youth_finance"

    # JWT
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # FSS API
    FSS_API_KEY: str = ""
    FSS_BASE_URL: str = "http://finlife.fss.or.kr/finlifeapi"

    # 온통청년 API
    YOUTH_POLICY_API_KEY: str = ""
    YOUTH_POLICY_BASE_URL: str = "https://www.youthcenter.go.kr/opi/empList.do"

    # Gemini
    GOOGLE_API_KEY: str = ""
    EMBEDDING_MODEL: str = "gemini-embedding-001"
    GENERATION_MODEL: str = "gemini-2.0-flash-lite"

    # FAISS
    FAISS_INDEX_PATH: str = "./data/policy_vector_index.faiss"
    POLICY_EMBED_PATH: str = "./data/policy_embeddings.csv"

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""


settings = Settings()

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Document Processing Service"
    
    # Database
    DATABASE_URL: str = "sqlite:///./app.db"  # Default to SQLite
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC: str = "documents"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 
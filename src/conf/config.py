from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_db: str = "postgres_db"
    postgres_user: str = "postgres_user"
    postgres_password: str = "postgres_password"
    postgres_port: int = 5432
    sqlalchemy_database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/todo_db"
    secret_key: str = "secret key"
    algorithm: str = "HS256"
    mail_username: str = "example@meta.ua"
    mail_password: str = "1111"
    mail_from: str = "example@meta.ua"
    mail_port: int = 465
    mail_server: str = "smtp.meta.ua"
    redis_host: str = "localhost"
    redis_port: int = 6379
    cloudinary_name: str = "cloudinary_name"
    cloudinary_api_key: str = "1111"
    cloudinary_api_secret: str = "1111"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
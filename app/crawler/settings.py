from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    path_to_screenshots: str = Field(default="screenshots", env="FLD_SCREENSHOTS")
    domains: list = ["www.avito.ru", ".avito.ru"]

    redis_host: str = Field(default="redis-ads", env="REDIS_HOST")
    redis_port: str = Field(default="6379", env="REDIS_PORT")
    redis_db: str = Field(default="0", env="REDIS_DB")

    db_host: str = Field(default="172.16.0.30", env="DB_HOST")
    db_port: str = Field(default="5439", env="DB_PORT")
    db_name: str = Field(default="ads", env="DB_NAME")
    db_schema: str = Field(default="public", env="DB_SCHEMA")
    db_username: str = Field(default="ads", env="DB_USERNAME")
    db_password: str = Field(default="ads", env="DB_PASSWORD")

    webdriver_executor = "http://webdriver:4444/wd/hub"

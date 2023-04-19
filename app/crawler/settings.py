#from datetime import datetime
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    folder_screenshots: str = Field(default='screenshots', env='FLD_SCREENSHOTS')
    domains: list = ['www.avito.ru', '.avito.ru']

    redis_host: str = Field(default='redis-ads', env='REDIS_HOST')
    redis_port: str = Field(default='6379', env='REDIS_PORT')
    redis_db: str = Field(default='0', env='REDIS_DB')

    db_host: str = Field(default='172.16.0.30', env='DB_HOST')
    db_port: str = Field(default='5439', env='DB_PORT')
    db_name: str = Field(default='ads', env='DB_NAME')
    db_username: str = Field(default='ads', env='DB_USERNAME')
    db_password: str = Field(default='ads', env='DB_PASSWORD')

# PATH_IMGS = "Z:\\" + str(datetime.today().strftime('%Y-%m-%d')) + "\\avito\\"
# DOMAINS = ['www.avito.ru', '.avito.ru']
# HOSTNAME = '172.16.0.39'
# USERNAME = 'crawler'
# PASSWORD = 'masterkey'
# DATABASE = 'crawler'

from pathlib import Path
from pydantic import SecretStr

from pydantic_settings import BaseSettings, SettingsConfigDict


class MySQLConnector(BaseSettings):
    mysql_db: SecretStr
    model_config = SettingsConfigDict(env_file=Path.cwd() / 'database' / '.env', env_file_encoding='utf-8')


connector = MySQLConnector()

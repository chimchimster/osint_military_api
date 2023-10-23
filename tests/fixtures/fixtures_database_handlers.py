from typing import Tuple

import pytest
import random
import string

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio.engine import create_async_engine

from pathlib import Path
from pydantic import SecretStr

from pydantic_settings import BaseSettings, SettingsConfigDict


class MySQLConnector(BaseSettings):
    mysql_db: SecretStr
    model_config = SettingsConfigDict(env_file=Path.cwd() / 'fixtures' / '.env', env_file_encoding='utf-8')


connector = MySQLConnector()


@pytest.fixture
async def get_mysql_engine():

    return create_async_engine(url=connector.mysql_db.get_secret_value())


@pytest.fixture
async def get_async_session(get_mysql_engine) -> sessionmaker.object_session:

    engine = await get_mysql_engine

    AsyncLocalSession = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    return AsyncLocalSession()


@pytest.fixture(scope='function')
async def generate_source_ids():

    source_ids = {574780907, 531705961, 464910380, 616886623}

    source_ids.update({random.choice(string.ascii_letters) for _ in range(100)})

    return source_ids


@pytest.fixture(scope='function')
async def generate_source_id():

    return random.randint(1, 4)


@pytest.fixture(scope='function')
async def generate_military() -> Tuple:
    from faker import Faker

    fake = Faker()

    military_name = fake.name()
    profile_info = fake.text()[:100]
    unit_id = random.randint(1, 4)

    return military_name, unit_id, profile_info

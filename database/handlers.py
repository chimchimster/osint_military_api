from typing import List, Final
from pathlib import Path
from random import choice

from sqlalchemy import select, insert

from osint_military_api.utils import get_vk_users_ids, read_schema
from .decorators import execute_transaction


TOKENS_PATH: Final[Path] = Path.cwd() / 'schemas' / 'tokens' / 'tokens.JSON'


@execute_transaction
async def check_if_profiles_exist(vk_screen_names: List[str]):

    pass


async def convert_vk_screen_name_to_source_id(vk_screen_names: List[str]) -> int:

    tokens = await read_schema(TOKENS_PATH, 'tokens')

    token = choice(tokens)
    print(token)
    vk_ids = await get_vk_users_ids(vk_screen_names, token=token)

    return vk_ids


from pathlib import Path
from random import choice
from typing import Final, List

from . import read_schema
from .decorators import do_post_request_to_vk_api

API_LINK: Final[str] = 'https://api.vk.com/method/'
TOKENS_PATH: Final[Path] = Path.cwd() / 'schemas' / 'tokens' / 'tokens.JSON'


@do_post_request_to_vk_api
async def get_vk_user_id(screen_name: str, **kwargs):

    token = kwargs.get('token')

    return await form_request_string(
        'users.get',
        user_ids=screen_name,
        access_token=token,
        v=5.154,
    )


async def form_request_string(method: str, **kwargs) -> str:

    kwargs = [f'{key}={val}&' for key, val in kwargs.items()]

    return API_LINK + """{}?{}""".format(method, ''.join(kwargs)[:-1])


async def convert_vk_screen_name_to_source_id(vk_screen_name: str) -> int:

    tokens = await read_schema(TOKENS_PATH, 'tokens')

    token = choice(tokens)

    vk_id = await get_vk_user_id(vk_screen_name, token=token)

    return vk_id

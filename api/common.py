import functools
from typing import Dict, Awaitable, Final, Union, List

from utils import *

VK_URL: Final[str] = 'https://vk.com/'
INST_URL: Final[str] = 'https://instagram.com/'


async def callback_handler(
        mapped_link_screen_name: Dict,
        coro: Union[functools.partial, Awaitable]
) -> Awaitable:
    return await iterate_over_callback_data(mapped_link_screen_name, coro)


async def iterate_over_callback_data(
        callback_data: Dict,
        coro: Union[functools.partial, Awaitable]
) -> Awaitable:
    for key, value in callback_data.items():
        if key.startswith(VK_URL):
            vk_source_id = await convert_vk_screen_name_to_source_id(value)
            response_model = VKResponse.model_validate(vk_source_id)

            if response_mdl := response_model.response:
                for response in response_mdl:
                    source_id = PersonID.model_validate(response).id

                    return await coro(source_id=source_id)
        elif key.startswith(INST_URL):
            return 1

        



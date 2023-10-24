import functools
from typing import Dict, Awaitable, Final, Union, List, Optional

from utils import *

VK_URL: Final[str] = 'https://vk.com/'
INST_URL: Final[str] = 'https://instagram.com/'


async def callback_handler(
        mapped_link_screen_name: Optional[Dict],
        vk_coro: Union[functools.partial, Awaitable],
        inst_coro: Optional[Union[functools.partial, Awaitable]]
) -> Awaitable:
    return await iterate_over_callback_data(
        mapped_link_screen_name,
        vk_coro=vk_coro,
        inst_coro=inst_coro,
    )


async def iterate_over_callback_data(
        callback_data: Optional[Dict],
        vk_coro: Optional[Union[functools.partial, Awaitable]],
        inst_coro: Optional[Union[functools.partial, Awaitable]],
) -> Awaitable:

    if not callback_data:
        await vk_coro()

    for key, value in callback_data.items():
        if key.startswith(VK_URL):
            vk_source_id = await convert_vk_screen_name_to_source_id(value)
            response_model = VKResponse.model_validate(vk_source_id)

            if response_mdl := response_model.response:
                for response in response_mdl:
                    source_id = PersonID.model_validate(response).id

                    return await vk_coro(source_id=source_id)
        elif key.startswith(INST_URL):

            return await inst_coro(screen_name=value)

        



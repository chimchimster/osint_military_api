import functools
from typing import Dict, Awaitable, Final, Union, List

from osint_military_api.utils import *


VK_URL: Final[str] = 'https://vk.com/'


async def vk_callback_handler(
        mapped_links_screen_names: Union[List[Dict], Dict],
        coro: Union[functools.partial, Awaitable]
) -> Awaitable:

    if isinstance(mapped_links_screen_names, Dict):
        return await iterate_over_callback_data(mapped_links_screen_names, coro)
    for mapped_link_screen_name in mapped_links_screen_names:
        mapped_link_screen_name: Dict
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
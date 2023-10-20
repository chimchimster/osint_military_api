from typing import List

from .decorators import do_post_request_to_vk_api


API_LINK = 'https://api.vk.com/method/'


@do_post_request_to_vk_api
async def get_vk_users_ids(screen_names: List[str], **kwargs) -> str:

    token = kwargs.get('token')

    return await form_request_string(
        'users.get',
        user_ids=','.join(screen_names),
        access_token=token,
        v=1.154,
    )


async def form_request_string(method: str, **kwargs) -> str:

    kwargs = [f'{key}={val}&' for key, val in kwargs.items()]

    return API_LINK + """{}?{}""".format(method, ''.join(kwargs)[:-1])


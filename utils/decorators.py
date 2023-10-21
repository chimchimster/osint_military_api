import sys
import json
import functools

from aiohttp import ClientSession


def do_post_request_to_vk_api(coro):
    @functools.wraps(coro)
    async def wrapper(*args, **kwargs):
        async with ClientSession() as session:

            request_string = await coro(*args, **kwargs)

            try:
                response = await session.post(request_string)

                response_str = await response.text()

                if response.status == 200:

                    return json.dumps(response_str)

            except Exception as e:
                sys.stdout.write(str(e))

    return wrapper

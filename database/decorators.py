import functools
import sys

from .async_session import AsyncLocalSession


def execute_transaction(coro):
    @functools.wraps(coro)
    async def wrapper(*args, **kwargs):

        async with AsyncLocalSession() as session:
            async with session.begin() as transaction:
                try:
                    result = await coro(*args, **kwargs, session=session)
                    await transaction.commit()
                    if result:
                        return result
                except Exception as e:
                    await transaction.rollback()
                    sys.stdout.write(str(e))

    return wrapper





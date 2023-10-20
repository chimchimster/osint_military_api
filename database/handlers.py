from sqlalchemy import select, insert

from .decorators import execute_transaction


@execute_transaction
async def check_if_profiles_exist():
    pass

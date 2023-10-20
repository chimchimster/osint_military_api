from fastapi import APIRouter

from .models import *

router = APIRouter()


@router.post('/account_add/')
async def add_account_handler(profiles: Profiles):

    return profiles

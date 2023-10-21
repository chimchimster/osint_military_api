from fastapi import APIRouter

from .models import *
from osint_military_api.utils import *
from osint_military_api.database import *

router = APIRouter()


@router.post('/account_add/')
async def add_account_handler(profiles: Profiles):

    validated_profiles = Profiles.model_validate(profiles)

    for profile in validated_profiles.profiles:

        profile = Profile.model_validate(profile)

        for link in profile.social_media_links:

            if link.startswith('https://vk.com/'):

                screen_name = link.split('https://vk.com/')

                res = await convert_vk_screen_name_to_source_id(screen_name)

                VKResponse.model_validate(res)

    return profiles

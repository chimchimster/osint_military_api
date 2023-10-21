from typing import Final

from fastapi import APIRouter

from .models import *
from osint_military_api.utils import *
from osint_military_api.database import *

router = APIRouter()


VK_URL: Final[str] = 'https://vk.com/'


@router.post('/account_add/')
async def add_account_handler(profiles: Profiles):

    validated_profiles = Profiles.model_validate(profiles)

    screen_names = []
    for profile in validated_profiles.profiles:

        profile = Profile.model_validate(profile)

        vk_ids = [''.join(link.split(VK_URL)) for link in profile.social_media_links if link.startswith(VK_URL)]
        screen_names.extend(vk_ids)

    result_response = await convert_vk_screen_names_to_source_ids(screen_names)
    validated_response = VKResponse.model_validate(result_response)

    source_ids = []
    for vk_obj in validated_response.response:
        validated_vk_obj = PersonID.model_validate(vk_obj)
        source_ids.append(validated_vk_obj.id)
    print(source_ids)
    return profiles

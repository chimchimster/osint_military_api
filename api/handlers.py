from typing import Final

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

        if mapped_links_screen_names := profile.social_media_links:
            for mapped_link_screen_name in mapped_links_screen_names:
                for key, value in mapped_link_screen_name.items():
                    if key.startswith('https://vk.com/'):
                        vk_source_id = await convert_vk_screen_name_to_source_id(value)
                        response_model = VKResponse.model_validate(vk_source_id)

                        if response_mdl := response_model.response:
                            for response in response_mdl:
                                source_id = PersonID.model_validate(response).id

                    else:
                        # Инстаграм пока что добавляем через базу
                        pass

    return profiles




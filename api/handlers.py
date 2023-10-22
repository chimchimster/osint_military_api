from typing import Final, Dict

from fastapi import APIRouter

from .models import *
from osint_military_api.utils import *
from osint_military_api.database import *

router = APIRouter()

VK_URL: Final[str] = 'https://vk.com/'


@router.post('/account_add/')
async def add_account_handler(profiles: Profiles):

    returning_exceptions = {}

    for profile in profiles.profiles:

        profile = Profile.model_validate(profile)

        if (mapped_links_screen_names := profile.social_media_links) is None:
            # Добавление профиля пользователя без аккаунтов
            await add_profile_into_database(profile, profiles.user_id)
        else:
            # Добавление профиля и его аккаунтов
            for mapped_link_screen_name in mapped_links_screen_names:
                mapped_link_screen_name: Dict
                for key, value in mapped_link_screen_name.items():
                    if key.startswith(VK_URL):
                        vk_source_id = await convert_vk_screen_name_to_source_id(value)
                        response_model = VKResponse.model_validate(vk_source_id)

                        if response_mdl := response_model.response:
                            for response in response_mdl:
                                source_id = PersonID.model_validate(response).id
                                has_exc = await add_profile_and_vk_account_into_database(
                                    profile=profile,
                                    source_id=source_id,
                                    soc_type=1,
                                    source_type=1,
                                    moderator_id=profiles.user_id
                                )
                                if has_exc:
                                    returning_exceptions[source_id] = Signals(has_exc).__str__()
                    else:
                        # Пока не обрабатываем инсту
                        pass

    return returning_exceptions


@router.post('/add_sources_to_existing_account/')
async def add_sources_to_existing_account_handler(account: Account):

    returning_exceptions = {}

    for link in account.accounts:
        link: Dict
        for key, value in link.items():
            if key.startswith(VK_URL):
                vk_source_id = await convert_vk_screen_name_to_source_id(value)
                response_model = VKResponse.model_validate(vk_source_id)

                if response_mdl := response_model.response:
                    for response in response_mdl:
                        source_id = PersonID.model_validate(response).id

                        has_exc = await add_account_to_existing_profile(
                            profile_id=account.profile_id,
                            source_id=source_id,
                            soc_type=1,
                            source_type=1,
                        )

                        if has_exc:
                            returning_exceptions[source_id] = Signals(has_exc).__str__()

            else:
                # Пока не обрабатываем инсту
                pass

    return returning_exceptions


@router.put('/change_account_belonging_to_profile/')
async def change_account_belonging_to_profile_handler():




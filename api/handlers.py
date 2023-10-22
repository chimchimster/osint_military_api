import json

from typing import Final, Dict

from fastapi import APIRouter

from .models import *
from osint_military_api.utils import *
from osint_military_api.database import *

router = APIRouter()

VK_URL: Final[str] = 'https://vk.com/'


@router.post('/account_add/')
async def add_account_handler(profiles: Profiles):

    returning_exceptions, returning_results = {}, {}

    for profile in profiles.profiles:

        profile = Profile.model_validate(profile)

        if (mapped_links_screen_names := profile.social_media_links) is None:
            # Добавление профиля пользователя без аккаунтов
            has_exc = await add_profile_into_database(profile, profiles.user_id)

            if has_exc in (Signals.PROFILE_ADDED,):
                returning_results[profile.full_name] = Signals(Signals.PROFILE_ADDED).__str__()
            else:
                returning_exceptions[profile.full_name] = Signals(has_exc).__str__()
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

                                if has_exc in (Signals.PROFILE_ADDED,):
                                    returning_results[key] = Signals(Signals.PROFILE_ADDED).__str__()
                                else:
                                    returning_exceptions[key] = Signals(has_exc).__str__()

                    else:
                        # Пока не обрабатываем инсту
                        pass

    response_dict = {
        'returning_results': returning_results,
        'returning_exceptions': returning_exceptions
    }

    response = json.dumps(response_dict)

    return response_dict


@router.post('/add_sources_to_existing_account/')
async def add_sources_to_existing_account_handler(account: Account):

    returning_exceptions, returning_results = {}, {}

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
                            moderator_id=account.user_id,
                        )

                        if has_exc in (Signals.SOURCE_ADDED,):
                            returning_results[key] = Signals(Signals.SOURCE_ADDED).__str__()
                        else:
                            returning_exceptions[key] = Signals(has_exc).__str__()
            else:
                # Пока не обрабатываем инсту
                pass

    response_dict = {
        'returning_results': returning_results,
        'returning_exceptions': returning_exceptions
    }

    response = json.dumps(response_dict)

    return response_dict


@router.put('/change_account_belonging_to_profile/')
async def change_account_belonging_to_profile_handler(account_profile_connection: AccountProfileConnection):

    returning_exceptions, returning_results = {}, {}

    if link := account_profile_connection.account:
        link: Dict

        for key, value in link.items():
            if key.startswith(VK_URL):
                vk_source_id = await convert_vk_screen_name_to_source_id(value)
                response_model = VKResponse.model_validate(vk_source_id)

                if response_mdl := response_model.response:
                    for response in response_mdl:
                        source_id = PersonID.model_validate(response).id

                        old_profile_id = account_profile_connection.old_profile_id
                        new_profile_id = account_profile_connection.new_profile_id

                        has_exc = await change_connection_between_profile_and_source(
                            old_profile_id=old_profile_id,
                            new_profile_id=new_profile_id,
                            source_id=source_id,
                            moderator_id=account_profile_connection.user_id,
                        )

                        if has_exc in (Signals.UPDATED_CONNECTION_BETWEEN_PROFILE_AND_SOURCE,):
                            returning_results[key] = Signals(
                                Signals.UPDATED_CONNECTION_BETWEEN_PROFILE_AND_SOURCE).__str__()
                        else:
                            returning_exceptions[key] = Signals(has_exc).__str__()
            else:
                # Инстаграм пока не обрабатываем
                pass

    response_dict = {
        'returning_results': returning_results,
        'returning_exceptions': returning_exceptions
    }

    response = json.dumps(response_dict)

    return response_dict


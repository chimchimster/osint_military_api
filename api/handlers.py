import json

from functools import partial
from typing import Final, Dict

from fastapi import APIRouter

from .models import *
from .common import vk_callback_handler
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

            coro = partial(
                add_profile_and_vk_account_into_database,
                profile=profile,
                soc_type=1,
                source_type=1,
                moderator_id=profiles.user_id,
            )

            has_exc = await vk_callback_handler(mapped_links_screen_names, coro)

            if has_exc in (Signals.PROFILE_ADDED,):
                returning_results[profile.full_name] = Signals(Signals.PROFILE_ADDED).__str__()
            else:
                returning_exceptions[profile.full_name] = Signals(has_exc).__str__()

    return {
        'returning_results': returning_results,
        'returning_exceptions': returning_exceptions
    }


@router.post('/add_sources_to_existing_account/')
async def add_sources_to_existing_account_handler(account: Account):
    returning_exceptions, returning_results = {}, {}

    if mapped_links_screen_names := account.accounts:

        # Добавление пользователя к существуюему профилю

        coro = partial(
            add_account_to_existing_profile,
            profile_id=account.profile_id,
            soc_type=1,
            source_type=1,
            moderator_id=account.user_id,
        )

        has_exc = await vk_callback_handler(mapped_links_screen_names, coro)

        if has_exc in (Signals.SOURCE_ADDED,):
            returning_results[account.profile_id] = Signals(Signals.SOURCE_ADDED).__str__()
        else:
            returning_exceptions[account.profile_id] = Signals(has_exc).__str__()

    return {
        'returning_results': returning_results,
        'returning_exceptions': returning_exceptions
    }


@router.put('/change_account_belonging_to_profile/')
async def change_account_belonging_to_profile_handler(account_profile_connection: AccountProfileConnection):
    returning_exceptions, returning_results = {}, {}

    if mapped_links_screen_names := account_profile_connection.account:

        # Изменение связи между профилем и его аккаунтами

        coro = partial(
            change_connection_between_profile_and_source,
            old_profile_id=account_profile_connection.old_profile_id,
            new_profile_id=account_profile_connection.new_profile_id,
            moderator_id=account_profile_connection.user_id,
        )

        has_exc = await vk_callback_handler(mapped_links_screen_names, coro)

        if has_exc in (Signals.UPDATED_CONNECTION_BETWEEN_PROFILE_AND_SOURCE,):
            returning_results[account_profile_connection.new_profile_id] = Signals(
                Signals.UPDATED_CONNECTION_BETWEEN_PROFILE_AND_SOURCE).__str__()
        else:
            returning_exceptions[account_profile_connection.old_profile_id] = Signals(has_exc).__str__()

    return {
        'returning_results': returning_results,
        'returning_exceptions': returning_exceptions
    }

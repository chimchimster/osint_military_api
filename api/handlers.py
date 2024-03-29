from functools import partial
from typing import Dict

from fastapi import APIRouter

from .models import *
from .common import callback_handler
from .frozens import *
from database import *

router = APIRouter()


@router.post('/account_add/')
async def add_account_handler(profiles: Profiles):

    returning_exceptions, returning_results = {}, {}

    for profile in profiles.profiles:

        profile = Profile.model_validate(profile)

        if (mapped_links_screen_names := profile.social_media_links) is None:

            # Добавление профиля пользователя без аккаунтов

            has_exc = await add_profile_into_database(profile, profiles.user_id)

            if has_exc in (Signals.PROFILE_ADDED,):
                returning_results[profile.full_name] = Signals(Signals.PROFILE_ADDED).name
            else:
                returning_exceptions[profile.full_name] = Signals(has_exc).name
        else:

            # Добавление профиля и его аккаунтов
            for mapped_link_screen_name in mapped_links_screen_names:

                vk_coro = partial(
                    add_profile_and_vk_account_into_database,
                    profile=profile,
                    soc_type=1,
                    source_type=1,
                    moderator_id=profiles.user_id,
                )

                inst_coro = partial(
                    add_profile_and_inst_account_into_database,
                    profile=profile,
                    moderator_id=profiles.user_id,
                )

                has_exc = await callback_handler(mapped_link_screen_name, vk_coro, inst_coro)

                if not has_exc:
                    return {'Произошла внутренняя ошибка, пожалуйста, повторите запрос.'}

                name = ''
                if isinstance(has_exc, tuple):
                    for h_e in has_exc:
                        name += Signals(h_e).name + ' '
                else:
                    name = Signals(has_exc).name

                server_response = SourcesAdd(
                    link=next(iter(mapped_link_screen_name)),
                    server_answer=name
                )

                if has_exc in (Signals.PROFILE_ADDED, (Signals.PROFILE_ADDED, Signals.SOURCE_ADDING_IN_PROCESSING)):
                    if profile.full_name not in returning_results:
                        returning_results[profile.full_name] = [server_response]
                    else:
                        returning_results[profile.full_name].append(server_response)
                else:

                    if profile.full_name not in returning_exceptions:
                        returning_exceptions[profile.full_name] = [server_response]
                    else:
                        returning_exceptions[profile.full_name].append(server_response)

    return {
        'returning_results': returning_results,
        'returning_exceptions': returning_exceptions
    }


@router.post('/add_sources_to_existing_account/')
async def add_sources_to_existing_account_handler(account: Account):

    returning_exceptions, returning_results = {}, {}

    if mapped_links_screen_names := account.accounts:
        for mapped_link_screen_name in mapped_links_screen_names:
            mapped_link_screen_name: Dict
            # Добавление пользователя к существуюему профилю

            vk_coro = partial(
                add_vk_account_to_existing_profile,
                profile_id=account.profile_id,
                soc_type=1,
                source_type=1,
                moderator_id=account.user_id,
            )

            inst_coro = partial(
                add_inst_account_to_existing_profile,
                profile_id=account.profile_id,
                moderator_id=account.user_id,
            )

            has_exc = await callback_handler(mapped_link_screen_name, vk_coro, inst_coro)

            if not has_exc:
                return {'Произошла ошибка, пожалуйста, повторите запрос.'}

            name = Signals(has_exc).name

            server_response = AccountAdd(
                link=next(
                    iter(mapped_link_screen_name)
                ),
                server_answer=name
            )

            if has_exc in (Signals.SOURCE_ADDED,):
                returning_results[account.profile_id] = Signals(Signals.SOURCE_ADDED).name
            else:

                if account.profile_id not in returning_exceptions:
                    returning_exceptions[account.profile_id] = [server_response]
                else:
                    returning_exceptions[account.profile_id].append(server_response)

    return {
        'returning_results': returning_results,
        'returning_exceptions': returning_exceptions
    }


@router.put('/change_account_belonging_to_profile/')
async def change_account_belonging_to_profile_handler(account_profile_connection: AccountProfileConnection):

    returning_exceptions, returning_results = {}, {}

    # Изменение связи между профилем и аккаунтом

    coro = partial(
        change_connection_between_profile_and_source,
        old_profile_id=account_profile_connection.old_profile_id,
        new_profile_id=account_profile_connection.new_profile_id,
        res_id=account_profile_connection.res_id,
        moderator_id=account_profile_connection.user_id,
    )

    has_exc = await callback_handler(None, coro, None)

    if not has_exc:
        return {'Произошла ошибка, пожалуйста, повторите запрос.'}

    name = Signals(has_exc).name

    server_response = AccountChange(
        res_id=account_profile_connection.res_id,
        server_answer=name,
    )

    if has_exc in (Signals.UPDATED_CONNECTION_BETWEEN_PROFILE_AND_SOURCE,):
        returning_results[account_profile_connection.new_profile_id] = server_response
    else:
        returning_exceptions[account_profile_connection.old_profile_id] = server_response

    return {
        'returning_results': returning_results,
        'returning_exceptions': returning_exceptions
    }

from typing import Optional, Union, Tuple

import sqlalchemy.exc
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from .decorators import execute_transaction
from osint_military_api.api import Profile
from .models import *
from .common import generate_hash
from .exceptions import Signals


@execute_transaction
async def add_profile_and_vk_account_into_database(
        profile: Profile = None,
        source_id: int = None,
        soc_type: int = None,
        source_type: int = None,
        moderator_id: int = None,
        **kwargs,
) -> Signals:

    if not all([profile, source_id, soc_type, source_type, moderator_id]):
        return Signals.BAD_REQUEST

    session = kwargs.get('session')

    has_source_id = await source_id_already_in_database(source_id, session)

    if has_source_id:
        return Signals.SOURCE_ID_EXISTS

    try:
        military_profile_id = await add_military_into_monitoring_profile(profile, session)
    except sqlalchemy.exc.IntegrityError:
        return Signals.PROFILE_EXISTS

    try:
        res_id = await add_source_id_into_source(source_id, soc_type, source_type, session)
    except sqlalchemy.exc.IntegrityError:
        return Signals.SOURCE_ID_EXISTS

    try:
        await create_connection_between_profile_and_res_id(military_profile_id, res_id, session)
    except sqlalchemy.exc.IntegrityError:
        return Signals.CONNECTION_PROFILE_SOURCE_EXISTS

    try:
        await create_connection_between_moderator_and_profile(moderator_id, military_profile_id, session)
    except sqlalchemy.exc.IntegrityError:
        return Signals.CONNECTION_MODERATOR_PROFILE_EXISTS

    return Signals.PROFILE_ADDED


@execute_transaction
async def add_profile_and_inst_account_into_database(
        profile: Profile = None,
        screen_name: str = None,
        moderator_id: int = None,
        **kwargs,
) -> Union[Tuple[Signals, Signals], Signals]:

    if not all([profile, moderator_id]):
        return Signals.BAD_REQUEST

    session = kwargs.get('session')

    try:
        military_profile_id = await add_military_into_monitoring_profile(profile, session)
    except sqlalchemy.exc.IntegrityError:
        return Signals.PROFILE_EXISTS

    try:
        await create_connection_between_moderator_and_profile(moderator_id, military_profile_id, session)
    except sqlalchemy.exc.IntegrityError:
        return Signals.CONNECTION_MODERATOR_PROFILE_EXISTS

    try:
        await add_account_into_source_inst_query(screen_name, military_profile_id, session)
    except sqlalchemy.exc.IntegrityError:
        return Signals.SOURCE_ID_EXISTS

    return Signals.PROFILE_ADDED, Signals.SOURCE_ADDING_IN_PROCESSING


@execute_transaction
async def add_profile_into_database(
        profile: Profile = None,
        moderator_id: int = None,
        **kwargs,
) -> Signals:

    if not all([profile, moderator_id]):
        return Signals.BAD_REQUEST

    session = kwargs.get('session')

    try:
        profile_id = await add_military_into_monitoring_profile(profile, session)
    except sqlalchemy.exc.IntegrityError:
        return Signals.PROFILE_EXISTS

    try:
        await create_connection_between_moderator_and_profile(moderator_id, profile_id, session)
    except sqlalchemy.exc.IntegrityError:
        return Signals.CONNECTION_MODERATOR_PROFILE_EXISTS

    return Signals.PROFILE_ADDED


@execute_transaction
async def add_vk_account_to_existing_profile(
        profile_id: int = None,
        source_id: int = None,
        soc_type: int = None,
        source_type: int = None,
        moderator_id: int = None,
        **kwargs,
) -> Signals:

    session = kwargs.get('session')

    if not all([profile_id, source_id, soc_type, source_type, moderator_id]):
        return Signals.BAD_REQUEST

    moderator_has_rights = await check_if_moderator_has_rights_to_bring_changes(profile_id, moderator_id, session)

    if not moderator_has_rights:
        return Signals.WRONG_MODERATOR_ID

    try:
        res_id = await add_source_id_into_source(source_id, soc_type, source_type, session)
    except sqlalchemy.exc.IntegrityError:
        return Signals.SOURCE_ID_EXISTS

    try:
        await create_connection_between_profile_and_res_id(profile_id, res_id, session)
    except sqlalchemy.exc.IntegrityError:
        return Signals.NO_MORE_THAN_ONE_ACCOUNT_FOR_PROFILE

    return Signals.SOURCE_ADDED


@execute_transaction
async def add_inst_account_to_existing_profile(
        screen_name: str = None,
        profile_id: int = None,
        moderator_id: int = None,
        **kwargs,
) -> Signals:

    session = kwargs.get('session')

    moderator_has_rights = await check_if_moderator_has_rights_to_bring_changes(profile_id, moderator_id, session)

    if not moderator_has_rights:
        return Signals.WRONG_MODERATOR_ID

    if not all([screen_name, moderator_id]):
        return Signals.BAD_REQUEST

    try:
        await add_account_into_source_inst_query(screen_name, profile_id, session)
    except sqlalchemy.exc.IntegrityError:
        return Signals.SOURCE_ID_EXISTS

    return Signals.SOURCE_ADDING_IN_PROCESSING


@execute_transaction
async def change_connection_between_profile_and_source(
        old_profile_id: int = None,
        new_profile_id: int = None,
        res_id: int = None,
        moderator_id: int = None,
        **kwargs,
) -> Signals:

    session = kwargs.get('session')

    moderator_has_rights = await check_if_moderator_has_rights_to_bring_changes(old_profile_id, moderator_id, session)

    if not moderator_has_rights:
        return Signals.WRONG_MODERATOR_ID

    if not all([old_profile_id, new_profile_id, res_id]):
        return Signals.BAD_REQUEST

    if not res_id:
        return Signals.NO_SUCH_RES_ID_IN_DATABASE

    has_exc = await check_if_connection_between_profile_and_source_exists(old_profile_id, res_id, session)

    if not has_exc:
        return Signals.NO_CONNECTION_BETWEEN_PROFILE_AND_PARTICULAR_SOURCE

    await update_connection_between_profile_and_source(
        old_profile_id,
        new_profile_id,
        res_id,
        session
    )

    return Signals.UPDATED_CONNECTION_BETWEEN_PROFILE_AND_SOURCE


async def add_account_into_source_inst_query(
        screen_name: str,
        profile_id: int,
        session: AsyncSession,
) -> None:
    insert_stmt = insert(SourceInstQuery).values(profile_id=profile_id, screen_name=screen_name)

    await session.execute(insert_stmt)


async def check_if_moderator_has_rights_to_bring_changes(
        profile_id: int,
        moderator_id: int,
        session: AsyncSession,
) -> Optional[UserMonitoringProfile]:

    select_stmt = select(UserMonitoringProfile).filter_by(id=moderator_id, profile_id=profile_id)

    has_rights = await session.execute(select_stmt)

    return has_rights.scalar()


async def update_connection_between_profile_and_source(
        old_profile_id: int,
        new_profile_id: int,
        res_id: int,
        session: AsyncSession,
) -> None:

    update_stmt = update(MonitoringProfileSource).filter_by(profile_id=old_profile_id, res_id=res_id).values(
        profile_id=new_profile_id
    )

    await session.execute(update_stmt)


async def get_res_id_of_source(source_id: int, session: AsyncSession) -> Optional[int]:

    select_stmt = select(Source.res_id).filter_by(source_id=source_id)

    res_id = await session.execute(select_stmt)

    return res_id.scalar()


async def check_if_connection_between_profile_and_source_exists(
        profile_id: int,
        res_id: int,
        session: AsyncSession,
) -> bool:

    select_stmt = select(MonitoringProfileSource).filter_by(
        profile_id=profile_id,
        res_id=res_id,
    )
    result = await session.execute(select_stmt)

    if result.scalar():
        return True
    return False


async def create_connection_between_moderator_and_profile(
        moderator_id: int,
        profile_id: int,
        session: AsyncSession
) -> None:

    insert_stmt = insert(UserMonitoringProfile).values(id=moderator_id, profile_id=profile_id)

    await session.execute(insert_stmt)


async def create_connection_between_profile_and_res_id(
        profile_id: int,
        res_id: int,
        session: AsyncSession,
) -> None:

    insert_stmt = insert(MonitoringProfileSource).values(profile_id=profile_id, res_id=res_id)

    await session.execute(insert_stmt)


async def add_military_into_monitoring_profile(
        profile: Profile,
        session: AsyncSession,
) -> Union[int, Signals]:

    """ :returns Profile.profile_id """

    insert_stmt = insert(MonitoringProfile).values(
        full_name=profile.full_name,
        unit_id=profile.unit_id,
        profile_info=profile.profile_info
    ).returning(MonitoringProfile.profile_id)

    profile = await session.execute(insert_stmt)

    return profile.scalar()


async def add_source_id_into_source(
        source_id: int,
        soc_type: int,
        source_type: int,
        session: AsyncSession
) -> int:

    insert_stmt = insert(Source).values(
        source_id=source_id,
        soc_type=soc_type,
        source_type=source_type,
    ).returning(Source.res_id)

    result = await session.execute(insert_stmt)

    return result.scalar()


async def source_id_already_in_database(source_id: int, session: AsyncSession) -> bool:

    select_stmt = select(Source.source_id).filter_by(source_id=source_id)

    result = await session.execute(select_stmt)

    db_source_id = result.scalar()

    if db_source_id:
        return True
    return False


@execute_transaction
async def get_auth_key_hash(moderator_id: int, **kwargs) -> Union[Signals, str]:

    session = kwargs.get('session')

    select_stmt = select(User.auth_key).filter_by(id=moderator_id)

    result = await session.execute(select_stmt)

    auth_key = result.scalar()

    if not auth_key:
        return Signals.NO_SUCH_MODERATOR_AUTH

    return await generate_hash(auth_key)







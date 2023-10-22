from typing import Optional, Union, Tuple

import sqlalchemy.exc
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from .decorators import execute_transaction
from osint_military_api.api import Profile
from .models import *
from .exceptions import Signals


@execute_transaction
async def add_profile_and_vk_account_into_database(
        profile: Profile = None,
        source_id: int = None,
        soc_type: int = None,
        source_type: int = None,
        moderator_id: int = None,
        **kwargs,
) -> Optional[Union[int, Signals, None]]:

    if not all([profile, source_id, soc_type, source_type, moderator_id]):
        return

    session = kwargs.get('session')

    has_source_id = await source_id_already_in_database(source_id, session)

    if has_source_id:
        return Signals.SOURCE_ID_EXISTS

    military_profile_id = await add_military_into_monitoring_profile(profile, session)

    res_id = await add_source_id_into_source(source_id, soc_type, source_type, session)

    await create_connection_between_profile_and_res_id(military_profile_id, res_id, session)
    await create_connection_between_moderator_and_profile(moderator_id, military_profile_id, session)


@execute_transaction
async def add_profile_into_database(
        profile: Profile = None,
        moderator_id: int = None,
        **kwargs,
) -> None:

    session = kwargs.get('session')

    profile_id = await add_military_into_monitoring_profile(profile, session)

    await create_connection_between_moderator_and_profile(moderator_id, profile_id, session)


@execute_transaction
async def add_account_to_existing_profile(
        profile_id: int = None,
        source_id: int = None,
        soc_type: int = None,
        source_type: int = None,
        **kwargs,
) -> Union[Optional[Signals]]:

    session = kwargs.get('session')

    try:
        res_id = await add_source_id_into_source(source_id, soc_type, source_type, session)
    except sqlalchemy.exc.IntegrityError:
        return Signals.SOURCE_ID_EXISTS

    try:
        await create_connection_between_profile_and_res_id(profile_id, res_id, session)
    except sqlalchemy.exc.IntegrityError:
        return Signals.NO_MORE_THAN_ONE_ACCOUNT_FOR_PROFILE

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
) -> int:
    """ :returns Profile.profile.id """
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







from typing import Optional

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from .decorators import execute_transaction
from osint_military_api.api import Profile
from .models import *


@execute_transaction
async def add_profile_into_database(
        profile: Profile,
        source_id: int,
        soc_type: int,
        source_type: int,
        **kwargs,
) -> Optional[int, None]:

    session = kwargs.get('session')

    has_source_id = await source_id_already_in_database(source_id, session)

    if has_source_id:
        return

    military_id = await add_military_into_monitoring_profile(profile, session)


    await add_source_id_into_source(source_id, soc_type, source_type, session)


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

    insert_stmt = insert(MonitoringProfile).values(
        full_name=profile.full_name,
        unit_id=profile.unit_id,
        profile_info=profile.profile_info
    )

    profile = await session.execute(insert_stmt)

    return profile.scalar().id


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
    )

    result = await session.execute(insert_stmt)

    return result.scalar().res_id


async def source_id_already_in_database(source_id: int, session: AsyncSession) -> bool:

    select_stmt = select(Source.source_id).filter_by(source_id=source_id)

    result = await session.execute(select_stmt)

    db_source_id = result.scalar()

    if db_source_id:
        return True
    return False







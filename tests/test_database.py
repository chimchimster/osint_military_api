from typing import Awaitable, Tuple

import pytest

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from . import *


@pytest.mark.asyncio
async def test_database_connection(get_async_session: AsyncSession):

    session = await get_async_session

    async with session:

        cnt = await session.connection()

        assert cnt is not None, 'Не удалось установить соединение с базой данных.'


@pytest.mark.asyncio
async def test_source_id_in_database(get_async_session: AsyncSession, generate_source_ids: Awaitable):

    source_ids = await generate_source_ids

    session = await get_async_session

    results = set()
    async with session:
        for source_id in source_ids:
            result = await session.execute(
                select(Source.source_id).filter_by(source_id=source_id)
            )

            result = result.scalar()

            if result:
                results.add(result)

    assert results == {574780907, 531705961, 464910380, 616886623}, 'Множество записей из базы данных невалидно.'


@pytest.mark.asyncio
async def test_add_source_id_into_source(get_async_session: AsyncSession, generate_source_id: Awaitable):

    session = await get_async_session

    source_id = await generate_source_id

    async with session:

        insert_stmt = insert(Source).values(source_type=1, soc_type=1, source_id=source_id).returning(Source.res_id)

        result = await session.execute(insert_stmt)

        result = result.scalar()

        assert result is not None, 'source_id не был добавлен в базу.'


@pytest.mark.asyncio
async def test_add_military_into_monitoring_profile(get_async_session: AsyncSession, generate_military: Awaitable):

    military_full_name, military_unit_id, military_profile_info = await generate_military

    session = await get_async_session

    async with session:
        insert_stmt = insert(MonitoringProfile).values(
            full_name=military_full_name,
            unit_id=military_unit_id,
            profile_info=military_profile_info,
        ).returning(MonitoringProfile.profile_id)

        result = await session.execute(insert_stmt)

        assert result.scalar() is not None, 'Профиль военнослужащего не был добавлен.'




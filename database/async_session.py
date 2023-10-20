from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from .engine import mysql_engine

AsyncLocalSession = sessionmaker(
    mysql_engine, class_=AsyncSession, expire_on_commit=False
)

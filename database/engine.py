from sqlalchemy.ext.asyncio import create_async_engine

from .config import connector


class MySQLEngine:
    db_url = connector.mysql_db.get_secret_value()
    engine = create_async_engine(db_url)


mysql_engine = MySQLEngine()

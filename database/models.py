from sqlalchemy import Column, Integer, BigInteger, String, Text
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Source(Base):

    __tablename__ = 'source'

    res_id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(BigInteger)
    soc_type = Column(Integer)
    source_type = Column(Integer)


class UserMonitoringProfile(Base):

    __tablename__ = 'user_monitoring_profile'

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, primary_key=True)


class MonitoringProfile(Base):

    __tablename__ = 'monitoring_profile'

    profile_id = Column(Integer, primary_key=True)
    full_name = Column(String(length=100))
    unit_id = Column(Integer)
    profile_info = Column(Text)


class MonitoringProfileSource(Base):

    __tablename__ = 'monitoring_profile_source'

    profile_id = Column(Integer, primary_key=True)
    res_id = Column(Integer, primary_key=True)


class SourceInstQuery(Base):

    __tablename__ = 'source_inst_query'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer)
    screen_name = Column(String(length=35))
    status = Column(String, default=None)


class User(Base):

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    auth_key = Column(String(length=32))


__all__ = [
    'Source',
    'User',
    'UserMonitoringProfile',
    'MonitoringProfile',
    'MonitoringProfileSource',
    'SourceInstQuery',
]

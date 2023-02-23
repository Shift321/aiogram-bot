from sqlalchemy import String, MetaData
from migrate.versioning.schema import Table, Column

from database.db import engine

db_engine = engine
db_meta = MetaData(bind=db_engine)

table = Table('cleaning', db_meta)
col = Column('week_day', String)
col.create(table)

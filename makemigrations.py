from sqlalchemy import String, MetaData
from migrate.versioning.schema import Table, Column

from database.db import engine

db_engine = engine
db_meta = MetaData(bind=db_engine)

table = Table('client', db_meta)
col = Column('cleaning_prefers', String)
col.create(table)

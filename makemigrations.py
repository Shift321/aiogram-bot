from sqlalchemy import MetaData,Date
from migrate.versioning.schema import Table, Column

from database.db import engine

db_engine = engine
db_meta = MetaData(bind=db_engine)

table = Table('client', db_meta)
col = Column('birth', Date)
col.create(table)

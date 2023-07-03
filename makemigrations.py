from sqlalchemy import String, MetaData, Integer, Date
from migrate.versioning.schema import Table, Column

from database.db import engine

db_engine = engine
db_meta = MetaData(bind=db_engine)

table = Table('wishes', db_meta)
col2 = Column('user_id', Integer)
col3 = Column('date_of_wish', Date)
col2.create(table)
col3.create(table)

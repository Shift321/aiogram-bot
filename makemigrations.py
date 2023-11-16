from sqlalchemy import String, MetaData, Integer, Date, Time
from migrate.versioning.schema import Table, Column

from database.db import engine

db_engine = engine
db_meta = MetaData(bind=db_engine)

table = Table('tvreserve', db_meta,
              Column('id', Integer, primary_key=True)
              )
col2 = Column('name', String)
col3 = Column('time_start', Time)
col4 = Column('time_end', Time)
col5 = Column('date', Date)
table.create()
col2.create(table)
col3.create(table)
col4.create(table)
col5.create(table)

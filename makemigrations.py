from sqlalchemy import MetaData, Date, Integer, String
from migrate.versioning.schema import Table, Column

from database.db import engine

db_engine = engine
db_meta = MetaData(bind=db_engine)

table = Table('client', db_meta)
col = Column('info_string', String)
col.create(table)

from database.db import session

raw = """CREATE TABLE dinner (
    id INTEGER PRIMARY KEY,
    food_id INTEGER REFERENCES food(id),
    first_course BOOLEAN DEFAULT FALSE,
    second_course BOOLEAN DEFAULT FALSE
);"""
session.execute(raw)

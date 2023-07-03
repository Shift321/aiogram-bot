from sqlalchemy import MetaData, Date, Integer, String
from migrate.versioning.schema import Table, Column

from database.db import session
from models.models import Wishes

row = "ALTER TABLE wishes ADD COLUMN user_id INTEGER"
row2 = "ALTER TABLE wishes ADD COLUMN date_of_wish DATE"

wishes = session.query(Wishes).all()

for i in wishes:
    session.delete(i)
    session.flush()
    session.commit()

session.execute(row)
session.execute(row2)

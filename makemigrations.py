from sqlalchemy import MetaData, Date, Integer, String
from migrate.versioning.schema import Table, Column

from database.db import session
from models.models import Wishes

row = """
ALTER TABLE wishes
ADD COLUMN user_id INTEGER,
ADD COLUMN date_of_wish DATE;


UPDATE wishes
SET user_id = 0, -- Specify the appropriate default value
    date_of_wish = '1970-01-01'; -- Specify the appropriate default date


ALTER TABLE wishes
DROP COLUMN name_of_user;


ALTER TABLE wishes
RENAME TO updated_wishes;"""


wishes = session.query(Wishes).all()

for i in wishes:
    session.delete(i)
    session.flush()
    session.commit()

session.execute(row)


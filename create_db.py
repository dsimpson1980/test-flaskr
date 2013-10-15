from sqlalchemy import create_engine
from config import SQLALCHEMY_DATABASE_URI

engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False)

with engine.connect() as conn:
    conn.execute(open('schema.sql', 'r').read())
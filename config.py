import os
import urlparse

urlparse.uses_netloc.append("postgres")

SQLALCHEMY_DATABASE_URI = os.environ["HEROKU_POSTGRESQL_CRIMSON_URL"]

SQLALCHEMY_ECHO = True
DEBUG = True
SECRET_KEY = 'development key'


#pagination
CUSTOMERS_PER_PAGE = 10
DEMAND_ITEMS_PER_PAGE = 10
PREMIUMS_PER_PAGE = 3
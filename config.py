import os
import urlparse

urlparse.uses_netloc.append('postgres')
SQLALCHEMY_DATABASE_URI = urlparse.urlparse(os.environ['DATABASE_URL'])
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_ECHO = True
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

#pagination
CUSTOMERS_PER_PAGE = 10
DEMAND_ITEMS_PER_PAGE = 10
PREMIUMS_PER_PAGE = 3
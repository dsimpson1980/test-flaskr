import os

DATABASE = HEROKU_POSTGRESQL_CRIMSON_URL
HOST = 'localhost'
USERNAME = 'mapdes'
PASSWORD = 'default'
SQLALCHEMY_DATABASE_URI = 'postgres://%s:%s@%s/%s' % (USERNAME, PASSWORD, HOST, DATABASE)
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_ECHO = True
DEBUG = True
SECRET_KEY = 'development key'


#pagination
CUSTOMERS_PER_PAGE = 10
DEMAND_ITEMS_PER_PAGE = 10
PREMIUMS_PER_PAGE = 3
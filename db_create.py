from groupbot.models import Base, db_DropEverything, drop_shit
from sqlalchemy import create_engine
from config import SQLALCHEMY_DATABASE_URI
from config import SQLALCHEMY_MIGRATE_REPO
from groupbot import db

# This script kills the database and then creates it again.  Purely for development, still haven't
# really implemented database migrations.

engine = create_engine(SQLALCHEMY_DATABASE_URI)
drop_shit()
# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
db.create_all()
# if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
#     api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
#     api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
# else:
#     api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))
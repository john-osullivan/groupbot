#----------------------------------------------------------------------------#
# Imports.
#----------------------------------------------------------------------------#

import os, sys

sys.path.append(os.getcwd())

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.heroku import Heroku
from flask.ext.script import Manager
import logging
from logging import Formatter, FileHandler
from config import TEST_DATABASE_URI

__all__ = ['controllers', 'views', 'models', 'forms', 'tests']

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)
heroku = Heroku(app)

def build_test_app():
    '''
    Builds the test version of the Flask app, registering SQLAlchemy on it.
    '''
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = TEST_DATABASE_URI
    db = SQLAlchemy(app)
    return (app, db)


import views, models, controllers

# Automatically tear down SQLAlchemy.
@app.teardown_request
def shutdown_session(exception=None):
    models.db_session.remove()

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s '
                                        '[in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    db.create_all()
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

#----------------------------------------------------------------------------#
# Create the user loader to let the LoginManager work correctly.
#----------------------------------------------------------------------------#
#----------------------------------------------------------------------------#
# Imports.
#----------------------------------------------------------------------------#

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.migrate import Migrate
from flask.ext.heroku import Heroku
import logging
from logging import Formatter, FileHandler

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
print "app.config: ", app.config
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
heroku = Heroku(app)

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

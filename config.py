import os
import subprocess

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Secret key for session management. You can generate random strings here:
# http://clsc.net/tools-old/random-string-generator.php
SECRET_KEY = 'my precious'

# Connect to the database
# SQLALCHEMY_DATABASE_URI = 'postgresql://johnosullivan:Rawrqed234@localhost/groupify_test'
print "About to try and connect to ", subprocess.check_output(['heroku config:get DATABASE_URL -a groupbot-app'])
SQLALCHEMY_DATABASE_URI = subprocess.check_output(['heroku config:get DATABASE_URL -a groupbot-app'])

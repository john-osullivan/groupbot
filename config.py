import os
import subprocess

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Secret key for session management. You can generate random strings here:
# http://clsc.net/tools-old/random-string-generator.php
SECRET_KEY = 'my precious'

# Connect to the Heroku Postgre database by grabbing the url out of the heroku config
# command.  That way we DEFINITELY know what the URL is.
# SQLALCHEMY_DATABASE_URI = 'postgresql://johnosullivan:Rawrqed234@localhost/groupify_test'
# database_url = subprocess.check_output(['heroku', 'config:get', 'DATABASE_URL', '-a', 'groupbot-app'], shell=True)
# print "About to try and connect to ", database_url
SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

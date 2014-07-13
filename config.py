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
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL','postgresql://johnosullivan:Rawrqed234@localhost/groupify_test')

# Once upon a time (7/12/2014) this was the URL to access the Heroku Postgres database.  I wanted
# to do it manually to run a database create.  Then nothing changed :(
# Keeping it here for now... JUST IN CASE.
# engine = create_engine('postgresql://aomarwxfityqsh:ChwDthtCANnyFKc0KegNQZjAWN@ec2-23-21-185-168.compute-1.amazonaws.com:5432/d8g1juqupb36dt')
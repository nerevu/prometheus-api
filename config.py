import os
from os import path as p

_basedir = p.dirname(__file__)


# configuration
class Content(object):
	heroku_app = 'prometheus-api'


class Config(Content):
	app = Content.heroku_app
	stage = os.environ.get('STAGE', False)
	end = '-stage' if stage else ''
	heroku = os.environ.get('DATABASE_URL', False)

	DEBUG = False
	ADMINS = frozenset(['reubano@gmail.com'])
	TESTING = False
	HOST = '127.0.0.1'
# 	PORT = int(os.environ.get('PORT', 5005))
	heroku_server = '%s%s.herokuapp.com' % (app, end)

	if heroku:
		SERVER_NAME = heroku_server
# 	else:
# 		SERVER_NAME = 'http://localhost:%s' % PORT

	SECRET_KEY = os.environ.get('SECRET_KEY', 'key')
	API_METHODS = ['GET', 'POST', 'DELETE', 'PATCH', 'PUT']
	API_ALLOW_FUNCTIONS = True
	API_ALLOW_PATCH_MANY = True
	API_MAX_RESULTS_PER_PAGE = 1000
	API_URL_PREFIX = ''


class Production(Config):
	defaultdb = 'postgres://reubano@localhost/app'
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', defaultdb)
	HOST = '0.0.0.0'
	BOOTSTRAP_USE_CDN = True
	BOOTSTRAP_FONTAWESOME = True


class Development(Config):
	SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % p.join(_basedir, 'app.db')
	DEBUG = True


class Test(Config):
	SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
	TESTING = True

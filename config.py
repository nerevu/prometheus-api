# -*- coding: utf-8 -*-
"""
    config
    ~~~~~~

    Provides the flask config options
    ###########################################################################
    # WARNING: if running on a a staging server, you MUST set the 'STAGE' env
    # heroku config:set STAGE=true --remote staging
    ###########################################################################
"""
from os import getenv, path as p
from pkutils import parse_module

PARENT_DIR = p.abspath(p.dirname(__file__))
app = parse_module(p.join(PARENT_DIR, 'app', '__init__.py'))
user = getenv('USER', 'user')

__APP_NAME__ = app.__package_name__
__EMAIL__ = app.__email__
__DOMAIN__ = 'api.prometheus.com'
__SUB_DOMAIN__ = __APP_NAME__.split('-')[-1]


class Config(object):
    HEROKU = getenv('DATABASE_URL', False)
    DEBUG = False
    TESTING = False
    DEBUG_MEMCACHE = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMINS = frozenset([__EMAIL__])
    HOST = '127.0.0.1'

    end = '-stage' if getenv('STAGE', False) else ''

    if HEROKU:
        SERVER_NAME = '{}{}.herokuapp.com'.format(__APP_NAME__, end)
    elif getenv('DIGITALOCEAN'):
        SERVER_NAME = '{}.{}'.format(__SUB_DOMAIN__, __DOMAIN__)
        SSLIFY_SUBDOMAINS = True

    SECRET_KEY = getenv('SECRET_KEY', 'secret')
    API_METHODS = ['GET', 'POST', 'DELETE', 'PATCH', 'PUT']

    API_ALLOW_FUNCTIONS = True
    API_ALLOW_PATCH_MANY = True
    API_RESULTS_PER_PAGE = 32
    API_MAX_RESULTS_PER_PAGE = 1024
    API_URL_PREFIX = ''
    SWAGGER_URL = ''
    SWAGGER_EXCLUDE_COLUMNS = ['utc_created', 'utc_updated']

    if HEROKU or getenv('DIGITALOCEAN'):
        SWAGGER_JSON = '{}/{}/swagger.json'.format(SERVER_NAME, API_URL_PREFIX)
    else:
        SWAGGER_JSON = '{}/swagger.json'.format(API_URL_PREFIX)


class Production(Config):
    db = __APP_NAME__.replace('-', '_')
    defaultdb = 'postgres://{}@localhost/{}'.format(user, db)
    DOMAIN = __DOMAIN__
    SQLALCHEMY_DATABASE_URI = getenv('DATABASE_URL', defaultdb)
    HOST = '0.0.0.0'


class Development(Config):
    base = 'sqlite:///{}?check_same_thread=False'
    SQLALCHEMY_DATABASE_URI = base.format(p.join(PARENT_DIR, 'app.db'))
    DEBUG = True
    DEBUG_MEMCACHE = False


class Test(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    DEBUG = True
    TESTING = True
    DEBUG_MEMCACHE = False

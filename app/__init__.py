# -*- coding: utf-8 -*-
"""
	app
	~~~~~~~~~~~~~~

	Provides the flask application
"""

from __future__ import print_function

import config

from inspect import isclass, getmembers
from importlib import import_module
from itertools import imap, repeat
from os import path as p, listdir
from savalidation import ValidationError
from flask import Flask

from sqlalchemy.exc import IntegrityError, OperationalError
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restless import APIManager

API_EXCEPTIONS = [
	ValidationError, ValueError, AttributeError, TypeError, IntegrityError,
	OperationalError]

db = SQLAlchemy()
__DIR__ = p.dirname(__file__)


def _get_modules(dir):
	dirs = listdir(dir)
	modules = [
		d for d in dirs if p.isfile(p.join(dir, d, '__init__.py'))
		and d != 'tests']

	return modules


def _get_app_classes(module):
	classes = getmembers(module, isclass)
	app_classes = filter(lambda x: str(x[1]).startswith("<class 'app"), classes)
	return ['%s' % x[0] for x in app_classes]


def create_app(config_mode=None, config_file=None):
	# Create webapp instance
	app = Flask(__name__)
	db.init_app(app)

	if config_mode:
		app.config.from_object(getattr(config, config_mode))
	elif config_file:
		app.config.from_pyfile(config_file)
	else:
		app.config.from_envvar('APP_SETTINGS', silent=True)

	@app.route('/')
	def home():
		return 'Welcome to the Prometheus API!'

	# Create the Flask-Restless API manager.
	mgr = APIManager(app, flask_sqlalchemy_db=db)

	kwargs = {
		'methods': app.config['API_METHODS'],
		'validation_exceptions': API_EXCEPTIONS,
		'allow_functions': app.config['API_ALLOW_FUNCTIONS'],
		'allow_patch_many': app.config['API_ALLOW_PATCH_MANY'],
		'max_results_per_page': app.config['API_MAX_RESULTS_PER_PAGE'],
		'url_prefix': app.config['API_URL_PREFIX']}

	# provides a nested list of class names grouped by model in the form [[],[]]
	# [[], ['Event', 'Type']]
	nested_classes = map(_get_app_classes, models)

	# provides a list of tuples (module, [list of class names])
	# in the form [(<module>,[]),(<module>,[])]
	# [(<module 'app.hermes.models' from '/path/to/models.pyc'>,
	# 	['Event', 'Type'])]
	sets = zip(models, nested_classes)

	# provides a nested iterator of classes in the expanded form of <class>
	# <class 'app.hermes.models.Event'>
	nested_tables = [imap(getattr, repeat(x[0]), x[1]) for x in sets]

	# Create API endpoints (available at /api/<tablename>)
	[[mgr.create_api(x, **kwargs) for x in tables] for tables in nested_tables]
	return app


# dynamically import app models and views
modules = _get_modules(__DIR__)
model_names = ['app.%s.models' % x for x in modules]
models = [import_module(x) for x in model_names]

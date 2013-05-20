# -*- coding: utf-8 -*-
"""
	app
	~~~~~~~~~~~~~~

	Provides the flask application
"""

from __future__ import print_function

import config
import helper

from inspect import isclass, getmembers
from itertools import imap, repeat
from savalidation import ValidationError
from flask import Flask, make_response, redirect
from json import JSONEncoder, dumps

from sqlalchemy.exc import IntegrityError, OperationalError
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restless import APIManager

API_EXCEPTIONS = [
	ValidationError, ValueError, AttributeError, TypeError, IntegrityError,
	OperationalError]

db = SQLAlchemy()


def _get_app_classes(module):
	classes = getmembers(module, isclass)
	app_classes = filter(lambda x: str(x[1]).startswith("<class 'app"), classes)
	return ['%s' % x[0] for x in app_classes]


def jsonify(result):
	response = make_response(dumps(result, cls=CustomEncoder))
	response.headers['Content-Type'] = 'application/json; charset=utf-8'
	response.headers['mimetype'] = 'application/json'
	response.headers['Access-Control-Allow-Origin'] = '*'
	return response


def create_app(config_mode=None, config_file=None):
	# Create webapp instance
	app = Flask(__name__)
	models = helper.get_models()
	db.init_app(app)

	if config_mode:
		app.config.from_object(getattr(config, config_mode))
	elif config_file:
		app.config.from_pyfile(config_file)
	else:
		app.config.from_envvar('APP_SETTINGS', silent=True)

	@app.route('/')
	def home():
		return redirect('http://docs.reubano.apiary.io/')

	@app.route('/reset/')
	def reset():
		db.drop_all()
		db.create_all()
		return jsonify({'objects': 'Database reset!'})

	@app.route('/keys/')
	def keys():
		return jsonify({'objects': helper.get_keys()})

	@app.route('/init_values/')
	def init_values():
		return jsonify({'objects': helper.get_init_values()})

	@app.route('/pop_values/')
	def pop_values():
		return jsonify({'objects': helper.get_pop_values()})

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


class CustomEncoder(JSONEncoder):
	def default(self, obj):
		if set(['quantize', 'year']).intersection(dir(obj)):
			return str(obj)
		elif set(['next', 'union']).intersection(dir(obj)):
			return list(obj)
		return JSONEncoder.default(self, obj)

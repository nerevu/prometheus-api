# -*- coding: utf-8 -*-
"""
    app
    ~~~

    Provides the flask application
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals)

from inspect import isclass, getmembers
from itertools import repeat
from functools import partial
from json import JSONEncoder, dumps
from os import path as p

import config

from savalidation import ValidationError
from flask import (
    Flask, make_response, redirect, Blueprint, send_from_directory,
    render_template)

from sqlalchemy.exc import IntegrityError, OperationalError
from flask_sqlalchemy import SQLAlchemy
from flask_restless import APIManager

from app import helper
from app.frs import Swaggerify
from builtins import *

__version__ = '0.17.0'

__title__ = 'prometheus-api'
__package_name__ = 'prometheus-api'
__author__ = 'Reuben Cummings'
__description__ = 'RESTful API for [prometheus](https://github.com/nerevu/prometheus), an asset allocation tool'
__email__ = 'reubano@gmail.com'
__license__ = 'MIT'
__copyright__ = 'Copyright 2017 Reuben Cummings'

API_EXCEPTIONS = [
    ValidationError, ValueError, AttributeError, TypeError, IntegrityError,
    OperationalError]

db = SQLAlchemy()
swag = Swaggerify()


def jsonify(result):
    response = make_response(dumps(result, cls=CustomEncoder))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.headers['mimetype'] = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


def create_app(config_mode=None, config_file=None):
    # Create webapp instance
    app = Flask(__name__)

    if config_mode:
        app.config.from_object(getattr(config, config_mode))
    elif config_file:
        app.config.from_pyfile(config_file)
    else:
        app.config.from_envvar('APP_SETTINGS', silent=True)

    skwargs = {
        'name': __title__, 'version': __version__,
        'description': __description__}

    swag.init_app(app, **skwargs)
    db.init_app(app)

    swag_config = {
        'dom_id': '#swagger-ui',
        'url': app.config['SWAGGER_JSON'],
        'layout': 'StandaloneLayout'}

    context = {
        'base_url': app.config['SWAGGER_URL'],
        'app_name': __package_name__,
        'config_json': dumps(swag_config)}

    @app.route('/')
    @app.route('/<path:path>')
    def home(path=None):
        if not path or path == 'index.html':
            return render_template('index.html', **context)
        else:
            print('showing {}'.format(path))
            return send_from_directory('static', path)

    @app.route('/reset/')
    def reset():
        db.drop_all()
        db.create_all()
        return jsonify({'objects': 'Database reset!'})

    @app.route('/keys/')
    def keys():
        tables = helper.gen_tables()
        return jsonify({'objects': dict(helper.get_col_names(tables))})

    @app.route('/init_values/')
    def init_values():
        return jsonify({'objects': helper.get_init_data()})

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

    create_api = partial(mgr.create_api, **kwargs)
    exclude = app.config['SWAGGER_EXCLUDE_COLUMNS']
    create_docs = partial(swag.create_docs, exclude_columns=exclude, **kwargs)

    with app.app_context():
        models = helper.get_models()

        for table in helper.gen_tables(models):
            create_api(table)
            create_docs(table)

    return app


class CustomEncoder(JSONEncoder):
    def default(self, obj):
        if set(['quantize', 'year']).intersection(dir(obj)):
            return str(obj)
        elif set(['next', 'union']).intersection(dir(obj)):
            return list(obj)
        return JSONEncoder.default(self, obj)

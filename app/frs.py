# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals)

try:
    from urllib import parse as urlparse
except ImportError:
    import urlparse

import re
import json
import yaml

from flask import jsonify, request, Blueprint, redirect

try:
    from flask_restless.helpers import get_related_model
except ImportError:
    get_related_model = None

from app.helper import get_plural, gen_columns

from builtins import *

SWAGGER_TYPES = {
    'BOOLEAN': 'bool',
    'INTEGER': 'integer',
    'SMALLINT': 'int32',
    'BIGINT': 'int64',
    'NUMERIC': 'number',
    'DECIMAL': 'number',
    'FLOAT': 'float',
    'REAL': 'float',
    'VARCHAR': 'string',
    'TEXT': 'string',
    'BLOB': 'binary',
    'BYTEA': 'binary',
    'BINARY': 'binary',
    'VARBINARY': 'binary',
    'DATE': 'date',
    'DATETIME': 'date-time',
    'INTERVAL': 'date-time',
    'ENUM': 'string',
}

JSON_TYPES = {
    'bool': 'boolean',
    'int32': 'integer',
    'int64': 'integer',
    'float': 'number',
    'binary': 'string',
    'date': 'string',
    'date-time': 'string',
    'password': 'string',
}


class Swaggerify(object):
    swagger = {
        'swagger': '2.0',
        'info': {},
        'tags': [],
        'schemes': ['http', 'https'],
        'basePath': '/',
        'consumes': ['application/json'],
        'produces': ['application/json'],
        'paths': {},
        'definitions': {}
    }

    def __init__(self, app=None, **kwargs):
        self.app = None

        if app is not None:
            self.init_app(app, **kwargs)

    def to_json(self, **kwargs):
        return json.dumps(self.swagger, **kwargs)

    def to_yaml(self, **kwargs):
        return yaml.dump(self.swagger, **kwargs)

    def __str__(self):
        return self.to_json(indent=4)

    @property
    def tags(self):
        return set(tag['name'] for tag in self.swagger['tags'])

    @tags.setter
    def tags(self, value):
        self.swagger['tags'] = value

    @property
    def version(self):
        if 'version' in self.swagger['info']:
            return self.swagger['info']['version']

        return None

    @version.setter
    def version(self, value):
        self.swagger['info']['version'] = value

    @property
    def title(self):
        if 'title' in self.swagger['info']:
            return self.swagger['info']['title']

        return None

    @title.setter
    def title(self, value):
        self.swagger['info']['title'] = value

    @property
    def description(self):
        if 'description' in self.swagger['info']:
            return self.swagger['info']['description']

        return None

    @description.setter
    def description(self, value):
        self.swagger['info']['description'] = value

    def add_path(self, table, methods=('GET',), **kwargs):
        name = table.__tablename__
        schema = table.__name__
        path = '{}/{}'.format(kwargs.get('url_prefix', ''), name)
        id_path = '{0}/{{{1}_id}}'.format(path, name)
        self.swagger['paths'][path] = {}

        if id_path not in self.swagger['paths']:
            self.swagger['paths'][id_path] = {}

        if table.__doc__:
            self.swagger['paths'][path]['description'] = table.__doc__

        for method in [m.lower() for m in methods]:
            if method == 'get':
                self.swagger['paths'][path][method] = {
                    'summary': 'list all {}'.format(get_plural(schema)),
                    'tags': [name],
                    'parameters': [
                        {
                            'name': 'q',
                            'in': 'query',
                            'description': 'query string',
                            'type': 'string'}],
                    'responses': {
                        200: {
                            'description': '{} list'.format(schema),
                            'schema': {
                                'type': 'array',
                                'items': {
                                    '$ref': '#/definitions/{}'.format(name)}}}}}

                self.swagger['paths'][id_path][method] = {
                    'summary': 'get {} by ID'.format(schema),
                    'tags': [name],
                    'parameters': [
                        {
                            'name': '{}_id'.format(name),
                            'in': 'path',
                            'description': '{} id'.format(schema),
                            'required': True,
                            'type': 'integer'}],
                    'responses': {
                        200: {
                            'description': 'Success',
                            'schema': {
                                '$ref': '#/definitions/{}'.format(name)}}}}
            elif method == 'delete':
                self.swagger['paths'][id_path][method] = {
                    'summary': 'delete {} by ID'.format(schema),
                    'tags': [name],
                    'parameters': [
                        {
                            'name': '{}_id'.format(name),
                            'in': 'path',
                            'description': '{} id to delete'.format(schema),
                            'required': True,
                            'type': 'integer'}],
                    'responses': {204: {
                        'description': '{} deleted'.format(schema)}}}
            elif method == 'post':
                self.swagger['paths'][path][method] = {
                    'summary': 'create a new {}'.format(schema),
                    'tags': [name],
                    'parameters': [
                        {
                            'name': 'body',
                            'in': 'body',
                            'description': '{} object to create'.format(schema),
                            'schema': {
                                '$ref': '#/definitions/{}_flat'.format(name)},
                            'required': True}],
                    'responses': {
                        201: {
                            'description': 'new {} created'.format(schema),
                            'schema': {
                                '$ref': '#/definitions/{}'.format(name)}}}}
            elif method == 'patch':
                self.swagger['paths'][id_path][method] = {
                    'summary': 'update {} by ID'.format(schema),
                    'tags': [name],
                    'parameters': [
                        {
                            'name': name,
                            'in': 'path',
                            'description': '{} id to update'.format(schema),
                            'type': 'integer'}],
                    'responses': {202: {
                        'description': '{} updated'.format(schema)}}}

        if name not in self.tags:
            tag = {'name': name, 'description': '{} operations'.format(schema)}
            self.swagger['tags'].append(tag)

    def add_defn(self, table, flat=False):
        name = table.__tablename__
        def_value = {'type': 'object', 'properties': {}}
        columns = dict(gen_columns(table))

        for column_name, column in sorted(columns.items()):
            excluded = column_name in self.exclude_columns
            is_id = column_name == 'id'
            is_related = not hasattr(column, 'type')

            if excluded or (flat and (is_id or is_related)):
                continue

            if is_related:
                related = get_related_model(table, column_name)
                related_name = related.__tablename__
                column_defn = {'$ref': '#/definitions/{}'.format(related_name)}

                if '{}_id'.format(column_name) not in columns:
                    column_defn = {'type': 'array', 'items': column_defn}
            else:
                column_type = str(column.type)

                if '(' in column_type:
                    column_type = column_type.split('(')[0]

                stype = SWAGGER_TYPES[column_type]

                if stype in JSON_TYPES:
                    column_defn = {'type': JSON_TYPES[stype], 'format': stype}
                else:
                    column_defn = {'type': stype}

            if column.__doc__:
                column_defn['description'] = column.__doc__

            def_value['properties'][column_name] = column_defn

        def_name = '{}{}'.format(name, '_flat' if flat else '')
        self.swagger['definitions'][def_name] = def_value

    def init_app(self, app, **kwargs):
        self.app = app
        swagger = Blueprint('swagger', __name__)

        if kwargs.get('name'):
            self.title = kwargs['name']

        if kwargs.get('version'):
            self.version = kwargs['version']

        if kwargs.get('description'):
            self.description = kwargs['description']

        @swagger.route('/swagger.json')
        def swagger_json():
            # Must have a request context
            self.swagger['host'] = urlparse.urlparse(request.url_root).netloc
            return jsonify(self.swagger)

        app.register_blueprint(swagger)

    def create_docs(self, table, **kwargs):
        self.exclude_columns = set(kwargs.get('exclude_columns', []))
        self.add_defn(table)
        self.add_defn(table, flat=True)
        self.add_path(table, **kwargs)

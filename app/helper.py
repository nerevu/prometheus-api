import re
from importlib import import_module
from inspect import isclass, getmembers
from os import path as p, listdir
from itertools import repeat
from flask import current_app as app
from datetime import datetime as dt, date as d
from sqlalchemy.orm.properties import RelationshipProperty as RelProperty

# dynamically import app models
def get_modules():
	dir = p.join(p.dirname(__file__), 'models')
	files = listdir(dir)
	modules = [
		f for f in files if (
			f.endswith('py') and not (f.endswith('pyc') or f.startswith('_')))]
	imports = ['app.models.%s' % p.splitext(x)[0] for x in modules]
	return [import_module(x) for x in imports]


def get_model_sets(modules):
	classes = getmembers(modules, isclass)
	return filter(lambda x: str(x[1]).startswith("<class 'app"), classes)


def get_model_classes(modules):
	set = get_model_sets(modules)
	return [x[1] for x in set]


def get_models(modules):
	set = get_model_sets(modules)
	return [x[0] for x in set]


# convert from CamelCase to camel_case
def convert(name):
	s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
	return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def get_plural(word):
	if word[-1] == 'y':
		return word[:-1] + 'ies'
	else:
		return word + 's'


def get_tables():
	bp_keys = [k for k in app.blueprints.keys() if k.endswith('api0')]
	tables = [k.replace('api0', '') for k in bp_keys]
	tables.sort()
	return tables


def get_keys():
	cols, tabs = [], []

	for m in get_models():
		classes = dir(m)

		for c in classes:
			try:
				fields = getattr(m, c).__table__.columns.keys()
				fields.sort()
				filtered = [
					f for f in fields if not (
						f.startswith('utc') or (
							f.startswith('id') and len(f) == 2))]

				cols.append(filtered)
				tabs.append(c)

			except AttributeError:
				pass

	tables = [convert(t) for t in tabs]
	keys = dict(zip(tables, cols))
	return keys


# use list of dicts because tables must be added in a particular order, e.g.,
# you have to add 'commodity_group' before 'commodity_type'
def get_init_values():
	return [
		{
		'exchange': [
			('New York Stock Exchange', 'NYSE'), ('NASDAQ', 'NASDAQ'),
			('Over the counter', 'OTC'), ('Currency', 'N/A')],
		'account_type': [(0, 'Brokerage'), (0, 'Roth IRA')],
		'commodity_group': [[('Security')], [('Currency')], [('Other')]],
		'company': [
			('', '', 'Scottrade', '', '', 'https://trading.scottrade.com/', ''),
			('', '', 'Vanguard', '', '', 'http://vanguard.com/', '')],
		'data_source': [[('Yahoo')], [('Google')], [('XE')]],
		'event_type': [
			[('Dividend')], [('Special Dividend')], [('Stock Split')],
			[('Name Change')], [('Ticker Change')]],
		'trxn_type': [('Buy', 'Buy'), ('Sell', 'Sell')]},
		{
		'commodity_type': [
			(1, 'Stock'), (1, 'Bond'), (1, 'Mutual Fund'), (1, 'ETF'),
			(2, 'Currency'), (3, 'Descriptor')]},
		{
		'commodity': [
			(3, 4, 'US Dollar', 'USD', 5),
			(3, 4, 'Euro', 'EUR', 5),
			(3, 4, 'Pound Sterling', 'GBP', 5),
			(3, 4, 'Canadian Dollar', 'CAD', 5),
			(3, 4, 'Multiple', 'Multiple', 6),
			(1, 1, 'Apple', 'AAPL', 1),
			(3, 4, 'Text', 'Text', 6)]},
		{
		'holding': [(1, 6, '')],
		'account': [
			(0, 1, 1, 0, 'Scottrade', 1, 0, 1),
			(0, 2, 1, 0, 'Vanguard IRA', 1, 0, 1)],
		'person': [
			('', 1, 'reubano@gmail.com', 'Reuben', 'Cummings', 0, 0, 0, '')]}]


def get_pop_values():
	return [{
		'commodity': [
			(1, 1, 'International Business Machines', 'IBM', 1),
			(1, 1, 'Wal-Mart', 'WMT', 1),
			(1, 1, 'Caterpillar', 'CAT', 1)],
		'holding': [(1, 8, ''), (1, 9, ''), (1, 10, '')]}]


def process(post_values, keys):
	tables = post_values.keys()
	value_list = post_values.values()
	key_list = [keys[t] for t in tables]
	combo = zip(key_list, value_list)

	table_data = [
		[dict(zip(c[0], values)) for values in c[1]] for c in combo]

	content_keys = ('table', 'data')
	content_values = zip(tables, table_data)
	return [dict(zip(content_keys, values)) for values in content_values]


def get_columns(model):
	"""Returns a dictionary-like object containing all the columns of the
	specified `model` class.

	"""
	return model._sa_class_manager


def get_req_columns(model):
	"""Returns a dictionary-like object containing all the columns of the
	specified `model` class.

	"""
	colums = model._sa_class_manager
	filtered = [
		c for c in colums if not (
			c.startswith('utc') or (c.startswith('id') and len(c) == 2))]

	return filtered

def get_relations(model):
	"""Returns a list of relation names of `model` (as a list of strings)."""
	cols = get_columns(model)
	return [k for k in cols if isinstance(cols[k].property, RelProperty)]


def get_type(c):
	if (
		c.startswith('id_') or c.endswith('_id') or (
			c.startswith('id') and len(c) == 2)):

		type = '<int>'
	elif (c.startswith('utc') or c.endswith('datetime')):
		type = '<datetime>'
	elif (c.startswith('date') or c.endswith('date')):
		type = '<date>'
	else:
		type = '<str>'

	return type


def doc_api(modules):
	cols, tables, models = repeat([], 3)
	resp = 'HOST: http://prometheus-api.herokuapp.com/\n\n'
	resp += '--- Prometheus API ---\n'

	for module in modules:
		models.extend(get_model_classes(module))

	for model in models:
		table = model.__name__
		plural_table = get_plural(table)
		end_point = model.__tablename__
		other, deep_other, related, deep_related, required = repeat('', 5)

		for column in get_columns(model):
			other += '\n  "%s": %s,' % (column, get_type(column))
			deep_other += '\n       "%s": %s,' % (column, get_type(column))

		for column in get_req_columns(model):
			required += '\n   "%s": %s,' % (column, get_type(column))

		# for relation in get_relations(model):
		# 	related += '\n    "%(c)s": %(c)s,' % {'c': relation}
		# 	deep_related += '\n         "%(c)s": %(c)s,' % {'c': relation}

		object = '{  %s\n}' % other
		deep_object = '     {        %s\n      }' % deep_other
		# TODO: add related fields to object

		json = '{\n  "total_pages": 1,\n  "objects": [\n%s\n  ],\n  "num_results": 1,\n  "page": 1\n}' % deep_object

		resp += '\n-- %s Resources --\n' % table
		resp += '\nList all %s\n' % plural_table
		resp += 'GET /%s\n' % end_point
		resp += '< 200\n< Content-Type: application/json\n'
		resp += '%s\n' % json
		resp += '\nList a particular %s\n' % table
		resp += 'GET /%s/{id}\n' % end_point
		resp += '< 200\n< Content-Type: application/json\n'
		resp += '%s\n' % object
		resp += '\nAdd new %s\n' % plural_table
		resp += 'POST /%s\n' % end_point
		resp += '> Content-Type: application/json\n'
		resp += '{%s\n}\n' % required
		resp += '< 201\n< Content-Type: application/json\n'
		resp += '{"id": <int>}\n'

	return resp
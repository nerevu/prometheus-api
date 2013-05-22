import re
from importlib import import_module
from os import path as p, listdir
from flask import current_app as app


# dynamically import app models
def get_modules(dir):
	files = listdir(dir)
	return [
		f for f in files if (
			f.endswith('py') and not (f.endswith('pyc') or f.startswith('_')))]


def get_models():
	dir = p.join(p.dirname(__file__), 'models')
	modules = get_modules(dir)
	models = ['app.models.%s' % p.splitext(x)[0] for x in modules]
	return [import_module(x) for x in models]


# convert from CamelCase to camel_case
def convert(name):
	s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
	return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


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

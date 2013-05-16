import re
from flask import current_app as app
from app import models


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

	for m in models:
		classes = dir(m)

		for c in classes:
			try:
				fields = getattr(m, c).__table__.columns.keys()
				filtered = [
					f for f in fields if not (
						f.startswith('utc') or (
							f.startswith('id') and len(f) == 2))]

				cols.append(set(filtered))
				tabs.append(c)

			except AttributeError:
				pass

	tables = [convert(t) for t in tabs]
	keys = dict(zip(tables, cols))
	return keys


# For flask-script
# use list of dicts because tables must be added in a particular order, e.g.,
# you have to add 'commodity_group' before 'commodity_type'
def get_init_values():
	return [
		{
		'exchange': [
			('NYSE', 'New York Stock Exchange'), ('NASDAQ', 'NASDAQ'),
			('OTC', 'Over the counter'), ('N/A', 'Currency')],
		'account_type': [(0, 'Brokerage'), (0, 'Roth IRA')],
		'commodity_group': [[('Security')], [('Currency')], [('Other')]],
		'company': [
			('https://trading.scottrade.com/', '', 'Scottrade', '', '', '', ''),
			('http://vanguard.com/', '', 'Vanguard', '', '', '', '')],
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
			('US Dollar', 4, 'USD', 3, 5),
			('Euro', 4, 'EUR', 3, 5),
			('Pound Sterling', 4, 'GBP', 3, 5),
			('Canadian Dollar', 4, 'CAD', 3, 5),
			('Multiple', 4, 'Multiple', 3, 6),
			('Apple', 1, 'AAPL', 2, 1),
			('Text', 4, 'Text', 3, 6)]},
		{
		'holding': [('', 1, 6)],
		'account': [
			(0, 'Scottrade', 1, 1, 1, 0, 0, 1),
			(0, 'Vanguard IRA', 2, 2, 1, 0, 0, 1)],
		'person': [
			(0, 'Reuben', 'Cummings', 1, '', 0, '', 0, 'reubano@gmail.com')]}]


def get_pop_values():
	return {
		'commodity': [
			('International Business Machines', 1, 'IBM', 1, 1),
			('Wal-Mart', 1, 'WMT', 1, 1),
			('Caterpillar', 1, 'CAT', 1, 1)],
		'holding': [('', 1, 8), ('', 1, 9), ('', 1, 10)]}


def process(post_values, keys):
	tables = post_values.keys()
	value_list = post_values.values()
	key_list = [keys[t] for t in tables]
	combo = zip(key_list, value_list)

	table_data = [
		[dict(zip(list[0], values)) for values in list[1]]
		for list in combo]

	content_keys = ('table', 'data')
	content_values = zip(tables, table_data)
	return [dict(zip(content_keys, values)) for values in content_values]

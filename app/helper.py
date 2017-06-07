# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals)

import re

from importlib import import_module
from inspect import isclass, getmembers
from os import path as p, listdir
from itertools import repeat
from json import loads

from flask import current_app as app
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.ext.hybrid import hybrid_property

from builtins import *

COLUMN_TYPES = (InstrumentedAttribute, hybrid_property)
JSON = 'application/json'
get_json = lambda r: loads(r.get_data(as_text=True))


def get_plural(word):
    if word[-1] == 'y':
        return word[:-1] + 'ies'
    else:
        return word + 's'


# dynamically import app models
def get_app_classes(module):
    classes = getmembers(module, isclass)
    app_classes = filter(lambda x: str(x[1]).startswith("<class 'app"), classes)
    return ['%s' % x[0] for x in app_classes]


def get_models():
    def filterer(file_name):
        py = file_name.endswith('py')
        pyc = file_name.endswith('pyc')
        return py and not (pyc or file_name.startswith('_'))

    module_dir = p.join(p.dirname(__file__), 'models')
    modules = [fn for fn in listdir(module_dir) if filterer(fn)]
    models = ['app.models.%s' % p.splitext(x)[0] for x in modules]
    return [import_module(x) for x in models]


def gen_tables(models):
    for model in models:
        for _cls in get_app_classes(model):
            yield getattr(model, _cls)


def get_table_names(tables):
    return [t.__tablename__ for t in tables]


def gen_columns(table, related=True):
    """Yields all the columns of the specified `table` class.

    This includes `hybrid attributes`_.
    .. _hybrid attributes: docs.sqlalchemy.org/en/latest/orm/extensions/hybrid.html
    """
    for superclass in table.__mro__:
        for name, column in superclass.__dict__.items():
            if isinstance(column, COLUMN_TYPES):
                if related or (not related and hasattr(column, 'type')):
                    yield (name, column)


def get_col_names(table):
    filterer = lambda name: not (name.startswith('utc') or name == 'id')
    _columns = gen_columns(table, False)
    return sorted(name for name, col in _columns if filterer(name))


# use list of dicts because tables must be added in a particular order, e.g.,
# you have to add 'commodity_group' before 'commodity_type'
def get_init_data():
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
            'trxn_type': [('Buy', 'Buy'), ('Sell', 'Sell')]
        }, {
            'commodity_type': [
                (1, 'Stock'), (1, 'Bond'), (1, 'Mutual Fund'), (1, 'ETF'),
                (2, 'Currency'), (3, 'Descriptor')]
        }, {
            'commodity': [
                (3, 4, 'US Dollar', 'USD', 5),
                (3, 4, 'Euro', 'EUR', 5),
                (3, 4, 'Pound Sterling', 'GBP', 5),
                (3, 4, 'Canadian Dollar', 'CAD', 5),
                (3, 4, 'Multiple', 'Multiple', 6),
                (1, 1, 'Apple', 'AAPL', 1),
                (3, 4, 'Text', 'Text', 6)]
        }, {
            'person': [
                ('', 1, 'reubano@gmail.com', 'Reuben', 'Cummings', 0, 0, 0, '')],
            'account': [
                (0, 1, 1, 0, 'Scottrade', 1, 0, 1),
                (0, 2, 1, 0, 'Vanguard IRA', 1, 0, 1)],
            'holding': [(1, 6, '')],
        }]


def get_pop_values():
    return [{
        'commodity': [
            (1, 1, 'International Business Machines', 'IBM', 1),
            (1, 1, 'Wal-Mart', 'WMT', 1),
            (1, 1, 'Caterpillar', 'CAT', 1)],
        'holding': [(1, 8, ''), (1, 9, ''), (1, 10, '')]}]


def process(raw):
    _tables = list(gen_tables(get_models()))
    tables = dict(zip(get_table_names(_tables), _tables))

    for data in raw:
        for table, values in data.items():
            columns = get_col_names(tables[table])
            table_data = [dict(zip(columns, row)) for row in values]
            yield {'table': table, 'data': table_data}

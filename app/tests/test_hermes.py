# -*- coding: utf-8 -*-
"""
    app.tests.test_hermes
    ~~~~~~~~~~~~~~~~~~~~~

    Provides unit tests for the :mod:`app.hermes` module.
"""

from json import loads, dumps

import pytest

from app import create_app, db
from app.helper import (
    get_table_names, get_models, process, get_init_values, gen_tables,
    get_keys, JSON, get_json)

@pytest.fixture
def client(request):
    app = create_app(config_mode='Test')
    client = app.test_client()
    models = get_models()
    tables = list(gen_tables(models))
    keys = dict(get_keys(tables))

    def get_num_results(table):
        r = client.get(client.prefix + table)
        return get_json(r)['num_results']

    def get_type(table):
        r = client.get('{}{}/1'.format(client.prefix, table))
        return get_json(r)['type']['id']

    client.prefix = app.config.get('API_URL_PREFIX', '')
    client.get_num_results = get_num_results
    client.get_type = get_type

    with app.test_request_context():
        db.create_all()
        client.tables = get_table_names(tables)
        content = [process(v, keys) for v in get_init_values()]

    for bundle in content:
        for piece in bundle:
            url = client.prefix + piece['table']

            for d in piece['data']:
                client.post(url, data=dumps(d), content_type=JSON)

    return client


def test_patch_commodity_exisiting_type(client):
    """Test for patching a commodity with an existing type using
    :http:method:`patch`.
    """
    table = 'commodity'
    init_type = client.get_type(table)
    types = client.get_num_results('commodity_type')

    # patch the first commodity with an existing type
    choices = range(1, types + 1)
    new = [x for x in choices if x != init_type][0]
    d = {'type': {'add': {'id': new}}}
    url = '{}{}/1'.format(client.prefix, table)
    r = client.patch(url, data=dumps(d), content_type=JSON)
    assert r.status_code == 200

    # test that the new commodity type was changed
    assert client.get_type(table) == new


def test_patch_commodity_new_type(client):
    """Test for patching a commodity with a new type using
    :http:method:`patch`.
    """
    table = 'commodity'
    init_type = client.get_type(table)
    types = client.get_num_results('commodity_type')

    # patch the commodity with a new type
    d = {'type': {'add': {'name': 'Brand New', 'group_id': 2}}}
    url = '{}{}/1'.format(client.prefix, table)
    r = client.patch(url, data=dumps(d), content_type=JSON)
    assert r.status_code == 200

    # test that the new commodity type was changed
    assert client.get_type(table) != init_type
    assert client.get_num_results('commodity_type') == types + 1


def test_post_event_new_type(client):
    """Test for posting an event using :http:method:`post`."""
    # check initial number of events and type
    types = client.get_num_results('event_type')
    events = client.get_num_results('event')

    # add event
    d = {
        'commodity_id': 3, 'date': '1/22/12',
        'type': {'name': 'Brand New'}, 'currency_id': 3, 'value': 100}

    url = '{}event'.format(client.prefix)
    r = client.post(url, data=dumps(d), content_type=JSON)
    assert r.status_code == 201

    # test that the new event and type were added
    assert client.get_num_results('event') == events + 1
    assert client.get_num_results('event_type') == types + 1


def test_post_price(client):
    """Test for posting a price using :http:method:`post`."""
    table = 'price'
    num = client.get_num_results(table)

    # add price
    d = {'commodity_id': 1, 'currency_id': 3, 'close': 30}
    r = client.post(client.prefix + table, data=dumps(d), content_type=JSON)
    assert r.status_code == 201

    # test that the new price was added
    assert client.get_num_results(table) == num + 1

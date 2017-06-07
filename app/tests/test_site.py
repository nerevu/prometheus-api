# -*- coding: utf-8 -*-
"""
    app.tests.test_site
    ~~~~~~~~~~~~~~

    Provides unit tests for the website.
"""

from json import loads, dumps

import pytest

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
        r = client.get(client.prefix + 'commodity_type')
        return get_json(r)['num_results']

    client.prefix = app.config.get('API_URL_PREFIX', '')
    client.get_num_results = get_num_results

    with app.test_request_context():
        db.create_all()
        client.tables = get_table_names(tables)
        client.content = [process(v, keys) for v in get_init_values()]

    return client


def test_home(client):
    r = client.get(client.prefix or '/')
    assert r.status_code == 200


def test_api_get(client):
    for bundle in client.content:
        for piece in bundle:
            url = client.prefix + piece['table']

            for d in piece['data']:
                r = client.post(url, data=dumps(d), content_type=JSON)
                assert r.status_code == 201

    for table in client.tables:
        assert client.get_num_results(table) >= 0


def test_api_delete(client):
    for table in client.tables:
        old = client.get_num_results(table)

        if old > 0:
            # delete entry and test that the it was deleted
            client.delete('{}{}/1'.format(client.prefix, table))
            assert client.get_num_results(table) == old - 1

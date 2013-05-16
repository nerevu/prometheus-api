# -*- coding: utf-8 -*-
"""
	app.tests.test_site
	~~~~~~~~~~~~~~

	Provides unit tests for the website.
"""

import nose.tools as nt

from . import APIHelper, get_globals, check_equal, loads, dumps, err
from pprint import pprint
from app import create_app, db


def setup_module():
	"""site initialization"""
	global initialized
	global client
	global tables
	global content

	client, tables, content = get_globals()
	db.create_all()
	initialized = True
	print('Site Module Setup\n')


class TestAPI(APIHelper):
	"""Unit tests for the API"""
	def __init__(self):
		self.cls_initialized = False

	def setUp(self):
		"""database initialization"""
		assert not self.cls_initialized
		db.create_all()

		for bundle in content:
			for piece in bundle:
				table = piece['table']
				data = piece['data']

				for d in data:
					r = self.post_data(d, table)
					nt.assert_equal(r.status_code, 201)

		self.cls_initialized = True
		print('\nTestAPI Class Setup\n')

	def tearDown(self):
		"""database removal"""
		assert self.cls_initialized
		db.drop_all()
		self.cls_initialized = False

		print('TestAPI Class Teardown\n')

	def test_api_get(self):
		for table in tables:
			self.setUp()
			n = self.get_num_results(table)
			self.tearDown()
			yield check_equal, table, n >= 0, True

	def test_api_delete(self):
		for table in tables:
			self.setUp()
			old = self.get_num_results(table)

			if old > 0:
				# delete first entry
				r = self.delete_data(table, 1)

				# test that the entry was deleted
				new = self.get_num_results(table)
				self.tearDown()
				yield check_equal, table, new, old - 1
			else:
				self.tearDown()


class TestWeb:
	"""Unit tests for the website"""
	def __init__(self):
		self.cls_initialized = False

	def test_home(self):
		r = client.get('/')
		nt.assert_equal(r.status_code, 200)

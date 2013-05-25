#!/usr/bin/env python
import os.path as p

from subprocess import call
from pprint import pprint

from app import create_app, db
from app.helper import doc_api, get_modules
from flask import current_app as app
from flask.ext.script import Manager

manager = Manager(create_app)
manager.add_option(
	'-m', '--cfgmode', dest='config_mode', default='Development')
manager.add_option('-f', '--cfgfile', dest='config_file', type=p.abspath)


@manager.command
def checkstage():
	"""Checks staged with git pre-commit hook"""
	path = p.join(p.dirname(__file__), 'app', 'tests', 'test.sh')
	cmd = "sh %s" % path
	return call(cmd, shell=True)


@manager.command
def runtests():
	"""Run nose tests"""
	cmd = 'nosetests -xv'
	return call(cmd, shell=True)


@manager.command
def createdb():
	"""Creates database if it doesn't already exist"""
	with app.app_context():
		db.create_all()

	print 'Database created'


@manager.command
def cleardb():
	"""Removes all content from database"""
	with app.app_context():
		db.drop_all()

	print 'Database cleared'


@manager.command
def resetdb():
	"""Removes all content from database and creates new tables"""
	with app.app_context():
		cleardb()
		createdb()


@manager.command
def docapi():
	print doc_api(get_modules())

if __name__ == '__main__':
	manager.run()

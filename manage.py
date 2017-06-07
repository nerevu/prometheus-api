#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

""" A script to manage development tasks """
from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

from os import path as p
from subprocess import call, check_call, CalledProcessError
from pprint import pprint

try:
    from urllib.parse import urlsplit, urlencode, parse_qs
except ImportError:
    from urlparse import urlsplit, urlencode, parse_qs

from app import create_app, db
from flask import current_app as app
from flask_script import Server, Manager

BASEDIR = p.dirname(__file__)
DEF_PORT = 5000

manager = Manager(create_app)
manager.add_option(
    '-m', '--cfgmode', dest='config_mode', default='Development')
manager.add_option('-f', '--cfgfile', dest='config_file', type=p.abspath)
manager.main = manager.run  # Needed to do `manage <command>` from the cli


@manager.option('-h', '--host', help='The server host')
@manager.option('-p', '--port', help='The server port')
@manager.option(
    '-t', '--threaded', help='Run multiple threads', action='store_true')
def runserver(live=False, offline=False, timeout=None, **kwargs):
    # Overriding the built-in `runserver` behavior
    """Runs the flask development server"""
    with app.app_context():
        if app.config.get('SERVER'):
            parsed = urlsplit(app.config['SERVER'])
            host, port = parsed.netloc, parsed.port or DEF_PORT
        else:
            host, port = app.config['HOST'], DEF_PORT

        kwargs.setdefault('host', host)
        kwargs.setdefault('port', port)

        server = Server(**kwargs)
        args = [
            app, server.host, server.port, server.use_debugger,
            server.use_reloader, server.threaded, server.processes,
            server.passthrough_errors]

        server(*args)


@manager.option('-h', '--host', help='The server host')
@manager.option('-p', '--port', help='The server port')
@manager.option('-o', '--offline', help='Offline mode', action='store_true')
@manager.option('-l', '--live', help='Use live data', action='store_true')
@manager.option('-T', '--timeout', help='Fetch timeout', type=int)
@manager.option(
    '-t', '--threaded', help='Run multiple threads', action='store_true')
def serve(**kwargs):
    # Alias for `runserver`
    """Runs the flask development server"""
    runserver(**kwargs)


@manager.command
def check():
    """Check staged changes for lint errors"""
    exit(call(p.join(BASEDIR, 'helpers', 'check-stage')))


@manager.option('-w', '--where', help='Modules to check')
@manager.option(
    '-s', '--strict', help='Check with pylint', action='store_true')
def lint(where, strict):
    """Check style with linters"""
    def_where = ['app', 'manage.py', 'config.py']
    extra = where.split(' ') if where else def_where

    args = [
        'pylint', '--rcfile=tests/standard.rc', '-rn', '-fparseable', 'app']

    try:
        check_call(['flake8'] + extra)
        check_call(args) if strict else None
    except CalledProcessError as e:
        exit(e.returncode)


@manager.option('-w', '--where', help='test path')
@manager.option(
    '-x', '--stop', help='Stop after first error', action='store_true')
@manager.option(
    '-f', '--failed', help='Run failed tests', action='store_true')
@manager.option(
    '-c', '--cover', help='Add coverage report', action='store_true')
@manager.option('-t', '--tox', help='Run tox tests', action='store_true')
@manager.option(
    '-d', '--detox', help='Run detox tests', action='store_true')
@manager.option(
    '-v', '--verbose', help='Use detailed errors', action='store_true')
@manager.option(
    '-p', '--parallel', help='Run tests in parallel in multiple processes',
    action='store_true')
@manager.option(
    '-D', '--debug', help='Use nose.loader debugger', action='store_true')
def test(where, stop, **kwargs):
    """Run nose, tox, and script tests"""
    opts = '-xv' if stop else '-v'
    opts += ' --with-coverage' if kwargs.get('cover') else ''
    opts += ' --last-failed' if kwargs.get('failed') else ''
    opts += ' --processes=-1' if kwargs.get('parallel') else ''
    opts += ' --detailed-errors' if kwargs.get('verbose') else ''
    opts += ' --debug=nose.loader' if kwargs.get('debug') else ''
    opts += ' -w %s' % where if where else ''

    try:
        if kwargs.get('tox'):
            check_call('tox')
        elif kwargs.get('detox'):
            check_call('detox')
        else:
            check_call('python -m pytest app/tests {}'.format(opts).split(' '))
    except CalledProcessError as e:
        exit(e.returncode)


@manager.command
def createdb():
    """Creates database if it doesn't already exist"""
    with app.app_context():
        db.create_all()

    print('Database created')


@manager.command
def cleardb():
    """Removes all content from database"""
    with app.app_context():
        db.drop_all()

    print('Database cleared')


@manager.command
def resetdb():
    """Removes all content from database and creates new tables"""
    with app.app_context():
        cleardb()
        createdb()


@manager.option('-r', '--remote', help='the heroku branch', default='staging')
def add_keys(remote):
    """Deploy staging app"""
    cmd = 'heroku keys:add ~/.ssh/id_rsa.pub --remote {}'
    check_call(cmd.format(remote).split(' '))


@manager.option('-r', '--remote', help='the heroku branch', default='staging')
def deploy(remote):
    """Deploy staging app"""
    branch = 'master' if remote == 'production' else 'features'
    cmd = 'git push origin {}'
    check_call(cmd.format(branch).split(' '))


if __name__ == '__main__':
    manager.run()

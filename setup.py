#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import sys
import pkutils

from os import path as p

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

PARENT_DIR = p.abspath(p.dirname(__file__))
paren = lambda *paths: p.join(PARENT_DIR, *paths)

sys.dont_write_bytecode = True
py2_requirements = set(pkutils.parse_requirements('py2-requirements.txt'))
py3_requirements = set(pkutils.parse_requirements('base-requirements.txt'))
dev_requirements = set(pkutils.parse_requirements('dev-requirements.txt'))
_prod_requirements = set(pkutils.parse_requirements('requirements.txt'))
readme = pkutils.read(paren('README.rst'))
module = pkutils.parse_module(paren('app', '__init__.py'))
license = module.__license__
version = module.__version__
project = module.__package_name__
description = module.__description__
user = 'reubano'

# Conditional sdist dependencies:
py2 = sys.version_info.major == 2
requirements = py2_requirements if py2 else py3_requirements
prod_requirements = _prod_requirements.difference(requirements)

# Conditional bdist_wheel dependencies:
py2_require = py2_requirements.difference(py3_requirements)

# Setup requirements
setup_require = [r for r in dev_requirements if 'pkutils' in r]

setup(
    name=project,
    version=version,
    description=description,
    long_description=readme,
    author=module.__author__,
    author_email=module.__email__,
    url=pkutils.get_url(project, user),
    download_url=pkutils.get_dl_url(project, user, version),
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    package_data={
        'app/templates': ['app/templates/*'],
        'app/static': ['app/static/*'],
    },
    install_requires=requirements,
    extras_require={
        'python_version<3.0': py2_require,
        'develop': dev_requirements,
    },
    setup_requires=setup_require,
    test_suite='nose.collector',
    tests_require=dev_requirements,
    license=license,
    zip_safe=False,
    keywords=[project] + description.split(' ') + ['finance', 'portfolio'],
    classifiers=[
        pkutils.LICENSES[license],
        pkutils.get_status(version),
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
		'Environment :: Web Environment',
		'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
		'Topic :: Database',
		'Topic :: Office/Business :: Financial :: Investment',
        'Intended Audience :: Developers',
		'Intended Audience :: Financial and Insurance Industry',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
    ],
    platforms=['MacOS X', 'Windows', 'Linux'],
)

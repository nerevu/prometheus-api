try:
	from setuptools import setup, find_packages
except ImportError:
	from distutils.core import setup, find_packages


with open('requirements.txt') as file:
	requirements = file.read().splitlines()


config = {
	'name': 'prometheus-api',
	'description': 'RESTful API for prometheus, a global asset allocation tool',
	'long_description': open('README.rst', 'rt').read(),
	'author': 'Reuben Cummings',
	'url': 'https://github.com/reubano/prometheus',
	'download_url':
		'https://github.com/reubano/prometheus/downloads/prometheus*.tgz',
	'author_email': 'reubano@gmail.com',
	'version': '0.16.1',
	'install_requires': requirements,
	'classifiers': ['Development Status :: 4 - Beta',
		'License :: OSI Approved :: The MIT License (MIT)',
		'Environment :: Web Environment',
		'Environment :: Console',
		'Intended Audience :: Developers',
		'Intended Audience :: Financial and Insurance Industry',
		'Topic :: Database',
		'Topic :: Office/Business :: Financial :: Investment',
		'Operating System :: MacOS :: MacOS X',
		'Operating System :: Microsoft :: Windows',
		'Operating System :: POSIX :: Linux'],
	'packages': find_packages(),
	'zip_safe': False,
	'license': 'MIT',
	'keywords': 'api, finance',
	'platforms' ['MacOS X', 'Windows', 'Linux'],
	'include_package_data': True}

setup(**config)

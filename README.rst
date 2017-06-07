prometheus-api |travis|
======================

.. |build| image:: https://secure.travis-ci.org/reubano/prometheus-api.png

.. |travis| image:: https://img.shields.io/travis/nerevu/prometheus-api/master.svg
    :target: https://travis-ci.org/nerevu/prometheus-api

Introduction
------------

`Prometheus-API <http://prometheus-api.herokuapp.com>`_ is the `Flask <http://flask.pocoo.org>`_ (`About Flask`_) powered RESTful API behind `Prometheus <http://prometheus.herokuapp.com>`_ (`About Prometheus`_).

Requirements
------------

Prometheus-API has been tested and known to work on the following configurations:

- MacOS X 10.9.5
- Ubuntu 14.04 LTS
- Python 2.7, 3.5, and 3.6

Framework
---------

Flask Extensions
^^^^^^^^^^^^^^^^

- Database abstraction with `SQLAlchemy <http://www.sqlalchemy.org>`_.
- Script support with `Flask-Script <http://flask-script.readthedocs.org/en/latest/>`_.
- Database validation with `SAValidation <https://pypi.python.org/pypi/SAValidation>`_
- RESTful API generation with `Flask-Restless <http://flask-restless.readthedocs.org/>`_

Production Server
^^^^^^^^^^^^^^^^^

- `PostgreSQL <http://postgresql.org/>`_
- `gunicorn <http://gunicorn.org/>`_
- `gevent <http://www.gevent.org/>`_

Quick Start
-----------

*Clone the repo*

.. code-block:: bash

    git clone git@github.com:reubano/prometheus-api.git

*Install requirements*

.. code-block:: bash

    cd prometheus-api
    pip install -r base-requirements.txt

*Run API server*

.. code-block:: bash

    manage serve

Now *view the API documentation* at ``http://localhost:5000``

Scripts
-------

Prometheus-API comes with a built in script manager ``manage.py``. Use it to start the
server, run tests, and initialize the database.

Usage
^^^^^

    manage <command> [command-options] [manager-options]

Examples
^^^^^^^^

*Start server*

    manage serve

*Run tests*

    manage test

*Run linters*

    manage lint

*Initialize the dev database*

    manage initdb

*Populate the production database*

    manage popdb -m Production

Manager options
^^^^^^^^^^^^^^^

::

      -m MODE, --cfgmode=MODE  set the configuration mode, must be one of
                               ['Production', 'Development', 'Test'] defaults
                               to 'Development'. See `config.py` for details
      -f FILE, --cfgfile=FILE  set the configuration file (absolute path)

Commands
^^^^^^^^

::

      checkstage  Checks staged with git pre-commit hook
      cleardb     Removes all content from database
      createdb    Creates database if it doesn't already exist
      initdb     Removes all content from database and creates new tables
      serve   Runs the Flask development server i.e. app.run()
      test    Run nose tests
      shell       Runs a Python shell inside Flask application context.

Command options
^^^^^^^^^^^^^^^

Type ``manage <command> -h`` to view any command's options

    manage manage serve -h

::

    usage: manage serve [-h] [-t HOST] [-p PORT] [--threaded]
                                 [--processes PROCESSES] [--passthrough-errors]
                                 [-d] [-r]

    Runs the Flask development server i.e. app.run()

    optional arguments:
      -h, --help              show this help message and exit
      -t HOST, --host HOST
      -p PORT, --port PORT
      --threaded
      --processes PROCESSES
      --passthrough-errors
      -d, --no-debug
      -r, --no-reload

Example
^^^^^^^

*Start production server on port 1000*

    manage serve -p 1000 -m Production

Configuration
-------------

Config Variables
^^^^^^^^^^^^^^^^

The following configurations settings are available in ``config.py``:

======================== ================================================================ =========================================
variable                 description                                                      default value
======================== ================================================================ =========================================
__YOUR_EMAIL__           your email address                                               <user>@gmail.com
API_METHODS              allowed HTTP verbs                                               ['GET', 'POST', 'DELETE', 'PATCH', 'PUT']
API_ALLOW_FUNCTIONS      allow sqlalchemy function evaluation                             TRUE
API_ALLOW_PATCH_MANY     allow patch requests to effect all instances of a given resource TRUE
API_MAX_RESULTS_PER_PAGE the maximum number of results returned per page                  1000
API_URL_PREFIX           string to prefix each resource in the api url                    ''
======================== ================================================================ =========================================

See the `Flask-Restless docs <http://flask-restless.readthedocs.org/en/latest/customizing.html>`_ for a complete list of settings.

Environment Variables
^^^^^^^^^^^^^^^^^^^^^

Prometheus-API will reference the ``SECRET_KEY`` environment variable in ``config.py`` if it is set on your system.

To set this environment variable, *do the following*:

    echo 'export SECRET_KEY=value' >> ~/.profile

Documentation
-------------

For a list of available resources, example requests and responses, and code samples,
view the `online documentation <https://prometheus-api.herokuapp.com/>`_. View the `Flask-Restless guide <http://flask-restless.readthedocs.org>`_ for more `request/response examples <http://flask-restless.readthedocs.org/en/latest/requestformat.html>`_ and directions on `making search queries. <http://flask-restless.readthedocs.org/en/latest/searchformat.html>`_

Services
----------

The Prometheus API is separated into different services, each responsible for performing a specific set of tasks.

======= =======================================================
service description
======= =======================================================
Hermes  price/event data aggregate
Cronus  portfolio performance analytics and allocation engine
Icarus  portfolio risk profiler *(coming soon)*
Oracle  random portfolio generator *(coming soon)*
Lynx    portfolio x-ray engine *(coming soon)*
Rosetta 3rd party portfolio data converter *(coming soon)*
======= =======================================================


Advanced Installation
---------------------

Virtual environment setup
^^^^^^^^^^^^^^^^^^^^^^^^^

Ideally, you should install python modules for every project into a `virtual environment <http://blog.sidmitra.com/manage-multiple-projects-better-with-virtuale>`_.
This setup will allow you to use different versions of the same module in different
projects without worrying about adverse interactions.

    sudo pip install virtualenv virtualenvwrapper

*Add the following* to your ``~/.profile``

.. code-block:: bash

    export WORKON_HOME=$HOME/.virtualenvs
    export PIP_VIRTUALENV_BASE=$WORKON_HOME
    export PIP_RESPECT_VIRTUALENV=true
    source /usr/local/bin/virtualenvwrapper.sh

*Create your new API virtualenv*

.. code-block:: bash

    cd prometheus-api
    mkvirtualenv --no-site-packages prometheus-api
    sudo easy_install pip
    sudo pip install -r base-requirements.txt


Production Server
^^^^^^^^^^^^^^^^^

Getting Gevent up and running is a bit tricky so follow these instructions carefully.

To use ``gevent``, you first need to install ``libevent``.

*Linux*

    apt-get install libevent-dev

*Mac OS X via* `homebrew <http://mxcl.github.com/homebrew/>`_

    brew install libevent

*Mac OS X via* `macports <http://www.macports.com/>`_

    sudo port install libevent

*Mac OS X via DMG*

    `download on Rudix <http://rudix.org/packages-jkl.html#libevent>`_

Now that libevent is handy, *install the remaining requirements*

    sudo pip install -r requirements.txt

Or via the following if you installed libevent from macports

.. code-block:: bash

    sudo CFLAGS="-I /opt/local/include -L /opt/local/lib" pip install gevent
    sudo pip install -r requirements.txt

Finally, *install foreman*

    sudo gem install foreman

Now, you can *run the application* locally

    foreman start

You can also *specify what port you'd prefer to use*

    foreman start -p 5555


Deployment
^^^^^^^^^^

If you haven't `signed up for Heroku <https://api.heroku.com/signup>`_, go
ahead and do that. You should then be able to `add your SSH key to
Heroku <http://devcenter.heroku.com/articles/quickstart>`_, and also
`heroku login` from the commandline.

*Install heroku and create your app*

.. code-block:: bash

    sudo gem install heroku
    heroku create -s cedar app_name

*Add the database*

.. code-block:: bash

    heroku addons:add heroku-postgresql:dev
    heroku pg:promote HEROKU_POSTGRESQL_COLOR

*Push to Heroku and initialize the database*

.. code-block:: bash

    git push heroku master
    heroku run python manage.py createdb -m Production

*Start the web instance and make sure the application is up and running*

.. code-block:: bash

    heroku ps:scale web=1
    heroku ps

Now, we can *view the application in our web browser*

    heroku open

And anytime you want to redeploy, it's as simple as ``git push heroku master``.
Once you are done coding, deactivate your virtualenv with ``deactivate``.

Directory Structure
-------------------

    tree . | sed 's/+----/├──/' | sed '/.pyc/d' | sed '/.DS_Store/d'

.. code-block:: bash

    prometheus-api
         ├──Procfile                        (heroku process)
         ├──README.rst                      (this file)
         ├──app
         |    ├──__init__.py                (main app module)
         |    ├──helper.py                  (manager/test helper functions)
         |    ├──LICENSE
         |    ├──MANIFEST.in                (pypi includes)
         |    ├──models
         |    |    ├──__init__.py
         |    |    ├──cronus.py             (portfolio analytics engine models)
         |    |    ├──hermes.py             (price/event data aggregator models)
         |    ├──README.rst                 (symlink for pypi)
         |    ├──setup.py                   (pypi settings)
         |    ├──tests
         |         ├──__init__.py           (main tests module)
         |         ├──standard.rc           (pylint config)
         |         ├──test.sh               (git pre-commit hook)
         |         ├──test_hermes.py        (hermes model tests)
         |         ├──test_site.py          (site tests)
         ├──app.db                          (app development database)
         ├──config.py                       (app config)
         ├──manage.py                       (flask-script)
         ├──requirements.txt                (python module requirements)
         ├──runtime.txt                     (python version)
         ├──schema.png                      (database relationship model)
         ├──setup.cfg                       (unit test settings)

Contributing
------------

*First time*

1. Fork
2. Clone
3. Code (if you are having problems committing because of git pre-commit
   hook errors, just run ``manage checkstage`` to see what the issues are.)
4. Use tabs **not** spaces
5. Add upstream ``git remote add upstream https://github.com/reubano/prometheus-api.git``
6. Rebase ``git rebase upstream/master``
7. Test ``manage test``
8. Push ``git push origin master``
9. Submit a pull request

*Continuing*

1. Code (if you are having problems committing because of git pre-commit
   hook errors, just run ``manage checkstage`` to see what the issues are.)
2. Use tabs **not** spaces
3. Update upstream ``git fetch upstream``
4. Rebase ``git rebase upstream/master``
5. Test ``manage test``
6. Push ``git push origin master``
7. Submit a pull request

Contributors
------------

    git shortlog -sn

.. code-block:: bash

    commits: 430
      430  Reuben Cummings

About Prometheus
----------------

Prometheus tells you how your stock portfolio has performed over time, gives insight into how to optimize your asset allocation, and monitors your portfolio for rebalancing or performance enhancing opportunities.

About Flask
-----------

`Flask <http://flask.pocoo.org>`_ is a BSD-licensed microframework for Python based on
`Werkzeug <http://werkzeug.pocoo.org/>`_, `Jinja2 <http://jinja.pocoo.org>`_ and good intentions.

License
-------

Prometheus API is distributed under the `BSD License <http://opensource.org/licenses/bsd-3-license.php>`_, the same as `Flask <http://flask.pocoo.org>`_ on which this program depends.

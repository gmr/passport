Passport
========
*Light weight configuration management using Consul*

Passport is a command line tool for rendering templates containing information
gained from Consul's Service Discovery API and Key/Value database.

|Version| |Downloads| |License|

Installation
------------
Passport is available via pypi_ and can be installed with easy_install or pip:

.. code:: bash

    pip install passport

Usage
-----
.. code:: bash

    usage: passport.py [-h] [--host HOST] [--port PORT] [--datacenter DATACENTER]
                       {kv,file} path destination
                            
Example
-------

As an example, the following template is stored in the KV database as
``templates/memcached/memcached.conf``

.. code:: python

    {% set nodes = ['%s:%s' % (r['Address'], r['ServicePort']) for r in consul.catalog.service('memcached')] %}

    [memcached]
        servers = {{ ','.join(nodes) }}

Invoking passport will render the file with a list of all memcached nodes to
``/etc/memcached.conf``.

.. code:: bash

    passport kv templates/memcached/memcached.conf /etc/memcached.conf

And the output would look something like:

.. code:: ini

[memcached]
    servers = 172.17.0.7:11211,172.17.0.8:11211

Template rendering is done via the `Tornado Template <https://tornado.readthedocs.org/en/latest/template.html>`_ engine.

Todo
----
- Add a *managed* mode where Passport will check for new services on a regular interval and when changes occur, update the rendered template and notify a process using HUP
- Add daemonization for managed mode
- Add the ability to specify pairs of templates/destinations in a single invocation

.. |Version| image:: https://badge.fury.io/py/passport.svg?
   :target: http://badge.fury.io/py/passport
  
.. |Downloads| image:: https://pypip.in/d/consulate/badge.svg?
   :target: https://pypi.python.org/pypi/passport
   
.. |License| image:: https://pypip.in/license/passport/badge.svg?
   :target: https://github.com/gmr/passport
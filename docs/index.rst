.. ttrss-python documentation master file, created by
   sphinx-quickstart on Wed Mar 27 09:06:50 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ttrss-python's documentation!
========================================

.. toctree::
   :maxdepth: 2

ttrss-python is a light-weight client library for the JSON API of Tiny Tiny RSS. 
Handling JSON in Python can be quite a pain, so this library abstracts all that
away to deliver Python object representations of categories, feeds and articles. 
Also, the specific calls and POST data sent to the server is handled automatically,
so that you can focus on the stuff that matters to your frontend application. 

Sounds good so far? Great, let's get started! 

Installation
============
This package is available at PyPI, so the easiest way to install is by doing a 
``pip install ttrss-python``. This will install the latest released version, as
well as all dependencies. Currently, the only dependency is the awesome Python
``requests`` library for handling all the http requests. 

If you for some reason can't or don't want to use ``pip``, just download the
tarball and run ``python setup.py install`` manually. 

It's highly recommended to use ``virtualenv`` for this (and any other for that 
matter!) installation. 

Basic usage
===========
The first thing you need to do is instantiate a ``TTRClient``. The constructor 
requires three arguments; URL, your username and your password::

    >>> from ttrss.client import TTRClient
    >>> client = TTRClient('http://url-to-tiny-tiny', 'username', 'super-secret-password')
    >>> client.login()

If you want the client to login automatically, as well as automatically refresh an expired 
session cookie, you may supply the optional keyword argument ``auto_login=True``. Note
that this may affect performance in a high-traffic client application, since it uses a
response hook to check every server response for a ``NOT_LOGGED_IN`` message::

    >>> client = TTRClient('http://url-to-tiny-tiny', 'username', 'super-secret-password', auto_login=True)

Categories
----------
Now you can retrieve a list of feed categories:: 

    >>> categories = client.get_categories()
    
To be continued... 


API Documentation
=================

This section will become more detailed over time as I add docstrings to the source code.

:mod:`client` module
--------------------

.. automodule:: ttrss.client
    :members:
    :undoc-members:
    :show-inheritance:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


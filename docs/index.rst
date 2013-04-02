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

Refer to the API docs for details on how to retrieve objects from the server.

Categories
----------
Category objects contain attributes describing the category, as well as a method to retrieve feeds
contained in it. Assuming a category object called ``cat``::

    >>> cat.title
    u'Example category'
    >>> cat.unread
    20
    >>> cat.id
    2

To retrieve a list of feeds belonging to this category, simply type::

    >>> cat.feeds()
    [<ttrss.client.Feed object at 0x103a0cfd0>, <ttrss.client.Feed object at 0x103478a50>]

The ``feeds`` method accepts parameters as well. Please refer to the API docs for details. 

Feeds
=====
Like category objects, feed objects contain metadata and a method to retrieve headlines::

    >>> feed.title
    u'MacRumors: Mac News and Rumors - All Stories'
    >>> feed.last_updated
    datetime.datetime(2013, 3, 24, 21, 18, 29)
    >>> feed.unread
    24
    >>> feed.feed_url
    u'http://feeds.macrumors.com/MacRumors-All'
    >>> feed.id
    5
    >>> feed.headlines()
    [<ttrss.client.Headline object at 0x103a0cfd0>, ...]

Headlines
=========
Headlines are short versions of articles. They too include all useful metadata::

    >>> headline.title
    u'Apple Acquires Indoor Mobile Location Positioning Firm WifiSLAM for $20 Million'
    >>> headline.excerpt
    u'The Wall Street Journal reports that Apple has acquired indoor location company WifiSLAM, paying aro&hellip;'
    >>> headline.link
    u'http://www.macrumors.com/2013/03/23/apple-acquires-indoor-mobile-location-positioning-firm-wifislam-for-20-million/'
    >>> headline.updated
    datetime.datetime(2013, 3, 24, 21, 18, 29)
    >>> headline.unread
    True
    >>> headline.tags
    [u'front page']
    >>> headline.published
    True
    >>> headline.labels
    []
    >>> headline.id
    1
    >>> headline.feed_id
    u'5'

To get the full article, simply type::

    >>> headline.full_article()
    <ttrss.client.Article object at 0x103a0cf90>

Articles
========
Article objects include all the useful information::

    >>> article.link
    u'http://www.macrumors.com/2013/03/23/apple-acquires-indoor-mobile-location-positioning-firm-wifislam-for-20-million/'
    >>> article.title
    u'Apple Acquires Indoor Mobile Location Positioning Firm WifiSLAM for $20 Million'
    >>> article.updated
    datetime.datetime(2013, 3, 24, 21, 18, 29)
    >>> article.comments
    u''
    >>> article.author
    u'Eric Slivka'
    >>> article.id
    1
    >>> article.unread
    True
    >>> article.content
    u"Lots of text... "

Article objects also include some useful methods for interaction::

    >>> article.publish()       # Publish to shared
    >>> article.toggle_unread() # Toggle unread status

You may also refresh the information about an article with fresh data from the server. This is useful if
you have a long-running script and interact with the server by other means while it's running::

    >>> article.unread
    True
    # Mark the article as read in the web interface or some other client...
    >>> article.refresh_status()
    >>> article.unread
    False


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


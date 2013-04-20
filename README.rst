ttrss-python - A Tiny Tiny RSS client library
=============================================

Have you ever wanted to write a python application to interface with your Tiny Tiny RSS server? Read on! 

At a glance
===========

Getting started is easy! Just type ``pip install ttrss-python`` in the virtualenv of your choice. 

Usage example:

:: 

    from ttrss.client import TTRClient
    client = TTRClient('http://url-to-rss-installation', 'username', 'super-secret-password', auto_login=True)
    cats = client.get_categories()
    cat = cats[0]
    cat.title
    u'News'
    feeds = cat.feeds()
    feed = feeds[0]
    feed.title
    u'MacRumors: Mac News and Rumors - All Stories'
    headlines = feed.headlines()
    # etc...

More detailed documentation can be found at https://ttrss-python.readthedocs.org/en/latest/

Development
===========
ttrss-python is still in early development and not yet feature complete. If there's a specific feature
you'd like me to prioritize, feel free to submit an issue or a pull request. 

The source code is available at https://github.com/Vassius/ttrss-python

Author
======
ttrss-python is written and maintained by Markus Wiik <vassius@gmail.com>.

Contribution & feedback
=======================
Contributions are welcome! Submit a pull request, file a bug report or write some docs if you'd like. 
Feature requests and other kinds of feedback are also appreciated. 

License
=======
ttrss-python is MIT licensed. See LICENSE for details. 


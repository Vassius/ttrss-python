from datetime import datetime
import requests
import json
from auth import TTRAuth
from exceptions import raise_on_error


class TTRClient(object):
    """
    This is the actual client interface to Tiny Tiny RSS.

    This object retains a http session with the needed session cookies. From
    the client you can fetch categories, feeds, headlines and articles, all
    represented by Python objects.  You can also update modify articles and
    feeds on the server.
    """
    def __init__(self, url, user=None, password=None, auto_login=False):
        """
        Instantiate a new client.

        :param url: The full URL to the Tiny Tiny RSS server, *without* the
        /api/ suffix.
        :param user: The username to use when logging in.
        :param password: The password for the user.
        :param auto_login: *Optional* Automatically login upon instantiation,
            and re-login
        when a session cookie expires.
        """
        self.sid = None
        self.url = url + '/api/'
        self.user = user
        self.password = password

        self._session = requests.Session()

        if auto_login:
            auth = TTRAuth(user, password)
            self._session.auth = auth

    def login(self):
        """
        Manually log in (i.e. request a session cookie)

        This method must be used if the client was not instantiated with
        ``auto_login=True``
        """
        r = self._get_json({
            'op': 'login',
            'user': self.user,
            'password': self.password
        })
        self.sid = r['content']['session_id']

    def logout(self):
        """
        Log out.

        After logging out, ``login()`` must be used to gain a valid session
        again. Please note that logging out invalidates any automatic
        re-login even after logging back in.
        """
        self._get_json({'op': 'logout'})
        self._session.auth = None

    def logged_in(self):
        r = self._get_json({'op': 'isLoggedIn'})
        return r['content']['status']

    def _get_json(self, post_data):
        if post_data['op'] == 'login':
            data = {}
        else:
            data = {'sid': self.sid}
        data.update(post_data)
        r = self._session.post(self.url, data=json.dumps(data))
        raise_on_error(r)
        return json.loads(r.content)

    def get_unread_count(self):
        """Get total number of unread articles"""
        r = self._get_json({'op': 'getUnread'})
        return int(r['content']['unread'])

    def get_feed_count(self):
        """Get total number of subscribed feeds."""
        r = self._get_json({'op': 'getCounters'})
        for c in r['content']:
            if c['id'] == u'subscribed-feeds':
                return int(c['counter'])
        return None

    def get_categories(
            self,
            unread_only=False,
            enable_nested=False,
            include_empty=False):
        """
        Get a list of all available categories

        :param unread_only: Only return categories containing unread articles.
            Defaults to ``False``.
        :param enable_nested: When enabled, traverse through sub-categories
            and return only the **topmost** categories in a flat list.
            Defaults to ``False``.
        :param include_empty: Include categories not containing any feeds.
            Defaults to ``False``. *Requires server version 1.7.6*
        """
        r = self._get_json({
            'op': 'getCategories',
            'unread_only': unread_only,
            'enable_nested': enable_nested,
            'include_empty': include_empty
        })
        return [Category(cat, self) for cat in r['content']]

    def get_feeds(
            self,
            cat_id=-1,
            unread_only=False,
            limit=0,
            offset=0,
            include_nested=False):
        """
        Get a list of feeds in a category.

        :param cat_id: Category id. This is available as the ``id`` property
            of a Category object.
        :param unread_only: *Optional* Include only feeds containing unread
            articles. Default is ``False``.
        :param limit: *Optional* Limit number of included feeds to ``limit``.
            Default is 0 (unlimited).
        :param offset: *Optional* Skip this number of feeds. Useful for
            pagination. Default is 0.
        :param include_nested: *Optional* Include child categories. Default
            is ``False``.
        """
        r = self._get_json({
            'op': 'getFeeds',
            'cat_id': cat_id,
            'unread_only': unread_only,
            'limit': limit,
            'offset': offset,
            'include_nested': include_nested
        })
        return [Feed(feed, self) for feed in r['content']]

    def get_labels(self):
        """Get a list of configured labels"""
        r = self._get_json({'op': 'getLabels'})
        return [Label(label, self) for label in r['content']]

    def get_headlines_for_label(self, label_id, **kwargs):
        """
        Get headlines for specified label id. Supports the same kwargs
            as ``get_headlines``, except for ``feed_id`` of course.
        """
        feed_id = -11 - int(label_id)
        return self.get_headlines(feed_id=feed_id, **kwargs)

    def get_headlines(
            self,
            feed_id=-4,
            limit=0,
            skip=0,
            is_cat=False,
            show_excerpt=True,
            show_content=False,
            view_mode=None,
            include_attachments=False,
            since_id=None,
            include_nested=True):

        """
        Get a list of headlines from a specified feed.

        :param feed_id: Feed id. This is available as the ``id`` property of
            a Feed object. Default is ``-4`` (all feeds).
        :param limit: Return no more than this number of headlines. Default is
            ``0`` (unlimited, though the server limits to 60).
        :param skip: Skip this number of headlines. Useful for pagination.
            Default is ``0``.
        :param is_cat: The feed_id is a category. Defaults to ``False``.
        :param show_excerpt: Include a short excerpt of the article. Defaults
            to ``True``.
        :param show_content: Include full article content. Defaults to
            ``False``.
        :param view_mode: (string = all_articles, unread, adaptive, marked,
            updated)
        :param include_attachments: include article attachments. Defaults to
            ``False``.
        :param since_id: Only include headlines newer than ``since_id``.
        :param include_nested: Include articles from child categories.
            Defaults to ``True``.
        """
        r = self._get_json({
            'op': 'getHeadlines',
            'feed_id': feed_id,
            'limit': limit,
            'skip': skip,
            'is_cat': is_cat,
            'show_excerpt': show_excerpt,
            'show_content': show_content,
            'view_mode': view_mode,
            'include_attachments': include_attachments,
            'since_id': since_id,
            'include_nested': include_nested,
        })
        return [Headline(hl, self) for hl in r['content']]

    def get_articles(self, article_id):
        """
        Get a list of articles from article ids.

        :param article_id: A comma separated string or list of article ids to
            fetch,
        """
        if isinstance(article_id, list):
            article_id = ",".join([str(i) for i in article_id])
        r = self._get_json({'op': 'getArticle', 'article_id': article_id})
        return [Article(article, self) for article in r['content']]

    def refresh_article(self, article):
        """
        Update all properties of an article object with fresh information from
        the server.

        Please note that this method alters the original object and does not
        return a new one.

        :param article: The article to refresh.
        """
        r = self._get_json({'op': 'getArticle', 'article_id': article.id})
        article.__init__(r['content'][0], client=self)

    def share_to_published(self, title, url, content):
        """
        Share an article to the *published* feed.

        :param title: Article title.
        :param url: Article url.
        :param content: Article content.
        """
        r = self._get_json({
            'op': 'shareToPublished',
            'title': title,
            'url': url,
            'content': content
        })

    def mark_unread(self, article_id):
        """
        Mark an article as unread.

        :param article_id: List or comma separated string of IDs of articles
            to mark as unread.
        """
        if isinstance(article_id, list):
            article_id = ",".join([str(i) for i in article_id])
        r = self._get_json({
            'op': 'updateArticle',
            'article_ids': article_id,
            'mode': 1,
            'field': 2
        })

    def mark_read(self, article_id):
        """
        Mark an article as read.

        :param article_id: List or comma separated string of IDs of articles
            to mark as read.
        """
        if isinstance(article_id, list):
            article_id = ",".join([str(i) for i in article_id])
        r = self._get_json({
            'op': 'updateArticle',
            'article_ids': article_id,
            'mode': 0,
            'field': 2
        })
        pass

    def toggle_unread(self, article_id):
        """
        Toggle the unread status of an article.

        :param article_id: List or comma separated string of IDs of articles
            to toggle unread.
        """
        if isinstance(article_id, list):
            article_id = ",".join([str(i) for i in article_id])
        r = self._get_json({
            'op': 'updateArticle',
            'article_ids': article_id,
            'mode': 2,
            'field': 2
        })

    def catchup_feed(self, feed_id, is_cat=False):
        """
        Attempt to mark all articles in specified feed as read.

        :param feed_id: id of the feed to catchup.
        :param is_cat: Specified feed is a category. Default is False.
        """
        r = self._get_json({
            'op': 'catchupFeed',
            'feed_id': feed_id,
            'is_cat': is_cat
        })

    def get_feed_count(self):
        """Return total number of feeds"""
        r = self._get_json({'op': 'getConfig'})
        return int(r['content']['num_feeds'])

    def update_daemon_running(self):
        """Return ``True`` if update daemon is running, ``False`` otherwise."""
        r = self._get_json({'op': 'getConfig'})
        return r['content']['daemon_is_running']

    def subscribe(self, feed_url, category_id=0, login=None, password=None):
        """Subscribe to specified feed.

        :param feed_url: URL to the feed to subscribe to.
        :param category_id: Place feed in the category with this ID.
        :param login: Login name for the feed, if any.
        :param password: Password for the feed, if any.
        """

        r = self._get_json({
            'op': 'subscribeToFeed',
            'feed_url': feed_url,
            'category_id': category_id,
            'login': login,
            'password': password
        })

    def unsubscribe(self, feed_id):
        """Unsubscribe to specified feed

        :param feed_id: ID of feed to unsubscribe.
        """

        r = self._get_json({'op': 'unsubscribeFeed', 'feed_id': feed_id})

    def get_pref(self, pref_name):
        """
        Return preference value of the specified key.

        :param pref_name: Name of the preference
        """
        r = self._get_json({'op': 'getPref', 'pref_name': pref_name})
        return r['content']['value']


class RemoteObject(object):
    """
    This is the base class for representing remote resources as Python objects.
    """
    def __init__(self, attr, client=None):
        self._client = client
        for key, value in attr.items():
            if key == 'id':
                value = int(value)
            self.__setattr__(key, value)


class Category(RemoteObject):
    def feeds(self, **kwargs):
        """
        Get a list of feeds for this category.

        :param unread_only: *Optional* Include only feeds containing unread
            articles. Default is ``False``.
        :param limit: *Optional* Limit number of included feeds to ``limit``.
            Default is 0 (unlimited).
        :param offset: *Optional* Skip this number of feeds. Useful for
            pagination. Default is 0.
        :param include_nested: *Optional* Include child categories. Default
            is ``False``.
        """
        return self._client.get_feeds(cat_id=self.id, **kwargs)


class Feed(RemoteObject):
    def __init__(self, attr, client):
        super(Feed, self).__init__(attr, client)
        try:
            self.last_updated = datetime.fromtimestamp(self.last_updated)
        except AttributeError:
            pass

    def catchup(self):
        """Mark this feed as read"""
        self._client.catchup_feed(self.id)

    def headlines(self, **kwargs):
        """
        Get a list of headlines from a this feed.

        :param limit: Return no more than this number of headlines. Default is
            ``0`` (unlimited, though the server limits to 60).
        :param skip: Skip this number of headlines. Useful for pagination.
            Default is ``0``.
        :param show_excerpt: Include a short excerpt of the article. Defaults
            to ``True``.
        :param show_content: Include full article content. Defaults to
            ``False``.
        :param view_mode: (string = all_articles, unread, adaptive, marked,
            updated)
        :param include_attachments: include article attachments. Defaults to
            ``False``.
        :param since_id: Only include headlines newer than ``since_id``.
        :param include_nested: Include articles from child categories.
            Defaults to ``True``.
        """
        return self._client.get_headlines(feed_id=self.id, **kwargs)


class Label(RemoteObject):
    def __init__(self, attr, client):
        super(Label, self).__init__(attr, client)

    def headlines(self, **kwargs):
        """
        Get a list of headlines for this label. Supports the same kwargs as
            ``Feed.headlines()``
        """
        return self._client.get_headlines_for_label(self.id)


class Headline(RemoteObject):
    """This class represents Headline objects. A headline is a short version
        of an article.
    """
    def __init__(self, attr, client):
        super(Headline, self).__init__(attr, client)
        try:
            self.updated = datetime.fromtimestamp(self.updated)
        except AttributeError:
            pass

    def full_article(self):
        """Get the full article corresponding to this headline"""
        r = self._client.get_articles(self.id)
        return r[0]


class Article(RemoteObject):
    def __init__(self, attr, client):
        super(Article, self).__init__(attr, client)
        try:
            self.updated = datetime.fromtimestamp(self.updated)
        except AttributeError:
            pass

    def publish(self):
        """Share this article to published feed"""
        self._client.share_to_published(self.title, self.link, self.content)

    def refresh_status(self):
        """Refresh this object with new data fetched from the server."""
        self._client.refresh_article(self)

    def toggle_unread(self):
        """Toggle unread status of this article"""
        self._client.toggle_unread(self.id)

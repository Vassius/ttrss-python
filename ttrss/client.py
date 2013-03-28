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
        r = self._session.post(self.url, data=json.dumps(post_data))
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

    def get_categories(self):
        """Get a list of all available categories"""
        r = self._get_json({'op': 'getCategories'})
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
        r = self._get_json({'op': 'getFeeds', 'cat_id': cat_id})
        return [Feed(feed, self) for feed in r['content']]

    def get_headlines(self, feed_id=0):
        """
        Get a list of headlines from a specified feed.

        :param feed_id: Feed id. This is available as the ``id`` property of
            a Feed object.
        """
        r = self._get_json({'op': 'getHeadlines', 'feed_id': feed_id})
        return [Headline(hl, self) for hl in r['content']]

    def get_articles(self, article_id):
        """
        Get a list of articles from article ids.

        :param article_id: A comma separated string of article ids to fetch.
        """
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

        :param article_id: ID of article to mark as unread.
        """
        r = self._get_json({
            'op': 'updateArticle',
            'article_ids': article_id,
            'mode': 1,
            'field': 2
        })

    def mark_read(self, article_id):
        """
        Mark an article as read.

        :param article_id: ID of article to mark as read.
        """
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

        :param article_id: ID of the article to toggle.
        """
        r = self._get_json({
            'op': 'updateArticle',
            'article_ids': article_id,
            'mode': 2,
            'field': 2
        })


class RemoteObject(object):
    def __init__(self, attr, client=None):
        self._client = client
        for key, value in attr.items():
            if key == 'id':
                value = int(value)
            self.__setattr__(key, value)


class Category(RemoteObject):
    def feeds(self, **kwargs):
        return self._client.get_feeds(cat_id=self.id, **kwargs)


class Feed(RemoteObject):
    def __init__(self, attr, client):
        super(Feed, self).__init__(attr, client)
        try:
            self.last_updated = datetime.fromtimestamp(self.last_updated)
        except AttributeError:
            pass

    def headlines(self):
        return self._client.get_headlines(feed_id=self.id)


class Headline(RemoteObject):
    def full_article(self):
        r = self._client.get_articles(self.id)
        return r[0]


class Article(RemoteObject):
    def publish(self):
        self._client.share_to_published(self.title, self.link, self.content)

    def refresh_status(self):
        self._client.refresh_article(self)

    def toggle_unread(self):
        self._client.toggle_unread(self.id)

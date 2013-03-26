from datetime import datetime
import time
import unittest
import requests
import json
import sys
sys.path.append('./')
from ttrss.client import TTRClient, Category, Feed, Headline, Article
from ttrss.exceptions import TTRNotLoggedIn, TTRAuthFailure

from test_data import TTR_URL, TTR_USER, TTR_PASSWORD

def get_ttr_client():
    return TTRClient(TTR_URL, user=TTR_USER, password=TTR_PASSWORD, auto_login=True)

def get_ttr_client_nologin():
    s = TTRClient(TTR_URL)
    s.username = TTR_USER
    s.password = TTR_PASSWORD
    return s

class TestRSSService(unittest.TestCase):

    def setUp(self):
        self.s = get_ttr_client_nologin()

    def test_session_existence(self):
        self.assertIsNotNone(self.s)

    def test_valid_url(self):
        r = requests.get(self.s.url)
        self.assertTrue(r.status_code == 200)

    def test_login(self):
        self.s.username
        self.s.password
        r = requests.post(self.s.url, data=json.dumps({'op': 'login', 'user': self.s.username, 'password': self.s.password}))
        data = json.loads(r.content)
        self.assertTrue(data['status'] == 0)

class TestApi(unittest.TestCase):
    def setUp(self):
        self.ttr = get_ttr_client()

    def test_auto_login(self):
        r = self.ttr._get_json({'op': 'getVersion'})
        self.assertIsInstance(r, dict)
        self.assertTrue(r['status'] == 0)

    def test_logout(self):
        self.ttr.logout()
        r = self.ttr._get_json({'op': 'isLoggedIn'})
        self.assertIsInstance(r, dict)
        self.assertFalse(r['status'])
        self.assertRaises(TTRNotLoggedIn, self.ttr._get_json, {'op': 'getVersion'})
    
    def test_manual_login(self):
        self.ttr.login()
        r = self.ttr._get_json({'op': 'getVersion'})
        self.assertIsInstance(r, dict)
        self.assertTrue(r['status'] == 0)

    def test_login_error(self):
        user = self.ttr.user
        self.ttr.user = ''
        self.assertRaises(TTRAuthFailure, self.ttr.login)
        self.ttr.user = user

class TestCategories(unittest.TestCase):
    def setUp(self):
        self.ttr = get_ttr_client()
        self.cat = self.ttr.get_categories()

    def test_get_categories(self):
        self.assertIsInstance(self.cat, list)
        self.assertTrue(len(self.cat) > 0)

    def test_category_object(self):
        c = self.cat[0]
        self.assertIsInstance(c, Category)
        self.assertTrue(c.unread > 0)
        c.title
        c.id

    def test_category_methods(self):
        c = self.cat[0]
        f = c.feeds()
        self.assertIsInstance(f, list)
        self.assertIsInstance(f[0], Feed)

class TestFeeds(unittest.TestCase):
    def setUp(self):
        self.ttr = get_ttr_client()
        feeds = self.ttr.get_feeds(cat_id=1)
        self.feed = feeds[0]

    def test_get_feeds(self): 
        feed = self.feed
        feed.id
        feed.title
        feed.unread
        self.assertIsInstance(feed.last_updated, datetime)

    def test_get_headlines(self):
        h = self.feed.headlines()
        self.assertIsInstance(h, list)
        self.assertIsInstance(h[0], Headline)


class TestHeadlines(unittest.TestCase):
    def setUp(self):
        self.ttr = get_ttr_client() 
        self.feed = self.ttr.get_feeds(cat_id=1)[0]

    def test_get_headlines(self):
        h = self.ttr.get_headlines(self.feed.id)
        self.assertIsInstance(h, list)
        h = h[0]
        self.assertIsInstance(h, Headline)
        h.title

    def test_get_article(self):
        h = self.ttr.get_headlines(self.feed.id)
        h = h[0]
        a = h.full_article()
        self.assertIsInstance(a, Article)
        self.assertEqual(a.id, h.id)
        
class TestArticles(unittest.TestCase):
    def setUp(self):
        self.ttr = get_ttr_client()
        feed = self.ttr.get_feeds(cat_id=1)[0]
        self.h = feed.headlines()[0]
        self.assertIsInstance(self.h, Headline)
        
    def test_get_article(self):
        a = self.ttr.get_articles(self.h.id)
        self.assertIsInstance(a, list)
        a = a[0]
        self.assertIsInstance(a, Article)
        self.assertEqual(a.id, self.h.id)

    def test_publish(self):
        a = self.ttr.get_articles(self.h.id)
        self.assertIsInstance(a, list)
        a = a[0]
        a.publish()
        h = self.ttr.get_headlines(feed_id=-2)
        l = [headline.link for headline in h]
        self.assertIn(a.link, l)

    def test_toggle_unread(self):
        a = self.ttr.get_articles(self.h.id)[0]
        unread = a.unread
        a.toggle_unread()
        a.refresh_status()
        self.assertFalse(unread == a.unread)
        a.toggle_unread()
        a.refresh_status()
        self.assertTrue(unread == a.unread)


class TestShare(unittest.TestCase):
    def setUp(self):
        self.ttr = get_ttr_client()

    def test_get_shared(self):
        h = self.ttr.get_headlines(feed_id=-2)
        self.assertIsInstance(h, list)
        self.assertIsInstance(h[0], Headline)

    def test_share_article(self):
        title = 'Testing publish' 
        url = 'http://{0}.com'.format(time.time())
        content = 'Test content'
        self.ttr.share_to_published(title, url, content)
        h = self.ttr.get_headlines(feed_id=-2)
        l = [headline.link for headline in h]
        self.assertIn(url, l)

class TestUpdate(unittest.TestCase):
    def setUp(self):
        self.ttr = get_ttr_client()
        self.article = self.ttr.get_articles(article_id=1)[0]

    def test_mark_unread(self):
        if self.article.unread:
            self.ttr.mark_read(self.article.id)
            a = self.ttr.get_articles(self.article.id)[0]
            self.assertFalse(a.unread)
        else:
            self.ttr.mark_unread(self.article.id)
            a = self.ttr.get_articles(self.article.id)[0]
            self.assertTrue(a.unread)

    def test_toggle_unread(self):
        a = self.ttr.get_articles(self.article.id)[0]
        unread = a.unread
        self.ttr.toggle_unread(a.id)
        a.refresh_status()
        self.assertFalse(a.unread == unread)


if __name__ == '__main__':
    unittest.main()



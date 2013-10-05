from datetime import datetime
import time
import unittest
import requests
import json
import sys
sys.path.insert(0, './')
from ttrss.client import TTRClient, Category, Feed, Headline, Article
from ttrss.exceptions import TTRNotLoggedIn, TTRAuthFailure

from test_data import TTR_URL, TTR_USER, TTR_PASSWORD

def get_ttr_client():
    return TTRClient(TTR_URL, user=TTR_USER, password=TTR_PASSWORD, auto_login=True)

def get_ttr_client_nologin():
    s = TTRClient(TTR_URL)
    s.user = TTR_USER
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
        self.s.user
        self.s.password
        r = requests.post(self.s.url, data=json.dumps({'op': 'login', 'user': self.s.user, 'password': self.s.password}))
        data = json.loads(r.text)
        self.assertTrue(data['status'] == 0)

class TestApi(unittest.TestCase):
    def setUp(self):
        self.ttr = get_ttr_client()

    def test_auto_login(self):
        r = self.ttr._get_json({'op': 'getVersion'})
        self.assertTrue(r['status'] == 0)
        r = self.ttr._get_json({'op': 'isLoggedIn'})
        self.assertIsInstance(r, dict)
        self.assertTrue(r['content']['status'])

    def test_logout(self):
        self.ttr.logout()
        r = self.ttr.logged_in()
        self.assertFalse(r)
        r = self.ttr._get_json({'op': 'isLoggedIn'})
        self.assertIsInstance(r, dict)
        self.assertFalse(r['status'])
        self.assertRaises(TTRNotLoggedIn, self.ttr._get_json, {'op': 'getVersion'})
    
    def test_manual_login(self):
        if self.ttr.logged_in():
            self.ttr.logout()
        self.ttr.login()
        r = self.ttr._get_json({'op': 'getVersion'})
        self.assertIsInstance(r, dict)
        self.assertTrue(r['status'] == 0)

    def test_login_error(self):
        user = self.ttr.user
        self.ttr.user = ''
        self.assertRaises(TTRAuthFailure, self.ttr.login)
        self.ttr.user = user

    def test_unread_count(self):
        r = self.ttr.get_unread_count()
        self.assertIsInstance(r, int)

    def test_update_daemon_running(self):
        r = self.ttr.update_daemon_running()
        self.assertTrue(r)

class TestCategories(unittest.TestCase):
    def setUp(self):
        self.ttr = get_ttr_client_nologin()
        self.ttr.login()
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
        self.ttr = get_ttr_client_nologin()
        self.ttr.login()
        cat = self.ttr.get_categories()[-1]
        feeds = self.ttr.get_feeds(cat.id)
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
        self.assertTrue(len(h) > 1)
        self.assertIsInstance(h[0], Headline)
        h_limited = self.feed.headlines(limit=len(h)-1)
        self.assertEqual(1, len(h) - len(h_limited))

    def test_get_feed_count(self):
        f = self.ttr.get_feed_count()
        self.assertIsInstance(f, int)

    def test_feed_catchup(self):
        self.assertTrue(self.feed.unread > 0)
        self.feed.catchup()
        cat = self.ttr.get_categories()[-1]
        feed = self.ttr.get_feeds(cat.id)[0]
        self.assertTrue(feed.unread == 0)

    def test_get_num_feeds(self):
        n = self.ttr.get_feed_count()
        self.assertTrue(n > 0)

    def test_subscribe_unsubscribe(self):
        f = self.ttr.get_feeds(cat_id=0)
        self.assertFalse(u'https://github.com/Vassius.atom' in [feed.feed_url for feed in f])
        self.ttr.subscribe(u'https://github.com/Vassius.atom')
        f = self.ttr.get_feeds(cat_id=0)
        self.assertTrue(u'https://github.com/Vassius.atom' in [feed.feed_url for feed in f])
        unsubscribe_id = None
        for feed in f:
            if feed.feed_url == u'https://github.com/Vassius.atom':
                unsubscribe_id = feed.id
                break
        self.ttr.unsubscribe(unsubscribe_id)
        f = self.ttr.get_feeds(cat_id=0)
        self.assertFalse(u'https://github.com/Vassius.atom' in [feed.feed_url for feed in f])

    def tearDown(self):
        h = self.feed.headlines()[-1]
        self.ttr.mark_unread(h.id)


class TestHeadlines(unittest.TestCase):
    def setUp(self):
        self.ttr = get_ttr_client_nologin() 
        self.ttr.login()
        cat = self.ttr.get_categories()[-1]
        self.feed = self.ttr.get_feeds(cat.id)[0]
        self.h = self.ttr.get_headlines(self.feed.id)

    def test_get_headlines(self):
        self.assertIsInstance(self.h, list)
        h = self.h[0]
        self.assertIsInstance(h, Headline)
        self.assertTrue(len(self.h) > 1)
        limited_h = self.ttr.get_headlines(self.feed.id, limit=len(self.h)-1)
        self.assertEqual(len(self.h) - len(limited_h), 1)
        h.title

    def test_get_article(self):
        h = self.h[0]
        a = h.full_article()
        self.assertIsInstance(a, Article)
        self.assertEqual(a.id, h.id)
        

class TestArticles(unittest.TestCase):
    def setUp(self):
        self.ttr = get_ttr_client_nologin()
        self.ttr.login()
        cat = self.ttr.get_categories()[-1]
        feed = self.ttr.get_feeds(cat.id)[0]
        self.headlines = feed.headlines()
        self.h = self.headlines[0]
        self.assertIsInstance(self.h, Headline)
        self.a = self.ttr.get_articles(self.h.id)
        
    def test_get_article(self):
        self.assertIsInstance(self.a, list)
        a = self.a[0]
        self.assertIsInstance(a, Article)
        self.assertEqual(a.id, self.h.id)

    def test_get_multiple_articles(self):
        h = self.headlines[-2:]
        a = self.ttr.get_articles("{0},{1}".format(h[0].id, h[1].id))
        a2 = self.ttr.get_articles([h[0].id, h[1].id])
        self.assertTrue(len(a) == 2)
        self.assertTrue(len(a2) == 2)

    def test_publish(self):
        self.assertIsInstance(self.a, list)
        a = self.a[0]
        a.publish()
        h = self.ttr.get_headlines(feed_id=-2)
        l = [headline.link for headline in h]
        self.assertIn(a.link, l)

    def test_toggle_unread(self):
        a = self.a[0]
        unread = a.unread
        a.toggle_unread()
        a.refresh_status()
        self.assertFalse(unread == a.unread)
        a.toggle_unread()
        a.refresh_status()
        self.assertTrue(unread == a.unread)

    def test_updated_timestamp(self):
        a = self.a[0]
        self.assertIsInstance(a.updated, datetime)


class TestShare(unittest.TestCase):
    def setUp(self):
        self.ttr = get_ttr_client_nologin()
        self.ttr.login()

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
        self.ttr = get_ttr_client_nologin()
        self.ttr.login()
        cat = self.ttr.get_categories()[1]
        feed = cat.feeds()[-1]
        self.article = feed.headlines()[-1].full_article()
#        self.article = self.ttr.get_articles()[-1]

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



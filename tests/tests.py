import unittest
import requests
import json
import sys
sys.path.append('./')
from ttr.client import TTRClient, Category

from test_data import TTR_URL, TTR_USER, TTR_PASSWORD

def get_ttr_client():
    return TTRClient(TTR_URL, TTR_USER, TTR_PASSWORD)

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
        r = self.ttr._get_json({'op': 'getVersion'})
        self.assertIsInstance(r, dict)
        self.assertTrue(r['status'] == 1)
    
    def test_manual_login(self):
        self.ttr.login()
        r = self.ttr._get_json({'op': 'getVersion'})
        self.assertIsInstance(r, dict)
        self.assertTrue(r['status'] == 0)

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

class TestFeeds(unittest.TestCase):
    def setUp(self):
        self.ttr = get_ttr_client()

    def test_get_feeds(self): 
        feeds = self.ttr.get_feeds()

if __name__ == '__main__':
    unittest.main()



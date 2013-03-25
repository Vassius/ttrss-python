import requests
import json

class TTRClient(object):
    def __init__(self, url, user=None, password=None):
        self.url = url + 'api/'
        self.user = user
        self.password = password

        self._session = requests.Session()

        if self.password and self.user:
            self.login()

    def login(self):
        self._session.post(self.url, data=json.dumps({'op': 'login', 'user': self.user, 'password': self.password}))

    def logout(self):
        self._get_json({'op': 'logout'})

    def _get_json(self, post_data):
        r = self._session.post(self.url, data=json.dumps(post_data))
        return json.loads(r.content)

    def get_categories(self):
        r = self._get_json({'op': 'getCategories'})
        return [Category(cat) for cat in r['content']]

    def get_feeds(self):
        r = self._get_json({'op': 'getFeeds', })

class Category(object):
    def __init__(self, cat):
        for key,value in cat.items():
            self.__setattr__(key, value)


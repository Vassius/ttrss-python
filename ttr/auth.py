from requests.auth import AuthBase
import requests
import json
from exceptions import raise_on_error

class TTRAuth(AuthBase):
    def __init__(self, user, password):
        self.user = user
        self.password = password

    def response_hook(self, r, **kwargs):
        j = json.loads(r.content)
        if int(j['status']) == 0:
            return r

        s = requests.Session()
        res = s.post(r.request.url, json.dumps({'op': 'login', 'user': self.user, 'password': self.password}))
        raise_on_error(res)

        _r = s.post(r.request.url, r.request.body)
        raise_on_error(_r)
        _r.headers.update(res.headers)

        return _r

    def __call__(self, r):
        r.register_hook('response', self.response_hook)
        return r

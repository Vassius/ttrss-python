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

        sid = None
        if r.headers['set-cookie']:
            sid = r.headers['set-cookie'].split(';')[0].split('=')[1]
            r.request.headers['Cookie'] = 'ttrss_api_sid={0}'.format(sid)
        else:
            sid = r.request.headers['Cookie'].split('=')[1]

        res = requests.post(r.request.url, json.dumps({
            'sid': sid,
            'op': 'login',
            'user': self.user,
            'password': self.password
        }))
        raise_on_error(res)

        r.request.deregister_hook('response', self.response_hook)
        _r = requests.Session().send(r.request)
        _r.cookies = r.cookies
        raise_on_error(_r)

        return _r

    def __call__(self, r):
        r.register_hook('response', self.response_hook)
        return r

from requests.auth import AuthBase
import requests
import json
from exceptions import raise_on_error


class TTRAuth(AuthBase):
    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.sid = None

    def response_hook(self, r, **kwargs):
        j = json.loads(r.content)
        if int(j['status']) == 0:
            return r

        self.sid = self._get_sid(r.request.url)

        r.request.deregister_hook('response', self.response_hook)
        j = json.loads(r.request.body)
        j.update({'sid': self.sid})
        req = requests.Request('POST', r.request.url)
        req.data = json.dumps(j)
        _r = requests.Session().send(req.prepare())
        raise_on_error(_r)

        return _r

    def __call__(self, r):
        r.register_hook('response', self.response_hook)
            
        data = json.loads(r.body)
        if 'sid' not in data:
            if self.sid is None:
                self.sid = self._get_sid(r.url)
            data.update({'sid': self.sid})
            req = requests.Request('POST', r.url)
            req.data = json.dumps(data)
            return req.prepare()
        else:
            self.sid = data['sid']
        return r

    def _get_sid(self, url):
        res = requests.post(url, data=json.dumps({
            'op': 'login',
            'user': self.user,
            'password': self.password
        }))
        raise_on_error(res)
        j = json.loads(res.content)
        return j['content']['session_id']

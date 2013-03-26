import json

class TTRAuthFailure(Exception):
    pass

class TTRNotLoggedIn(Exception):
    pass

def raise_on_error(r):
    j = json.loads(r.content)
    if int(j['status']) == 0:
        return

    if j['content']['error'] == 'NOT_LOGGED_IN':
        raise TTRNotLoggedIn

    if j['content']['error'] == 'LOGIN_ERROR':
        raise TTRAuthFailure


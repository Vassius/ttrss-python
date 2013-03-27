import json


class TTRAuthFailure(Exception):
    pass


class TTRNotLoggedIn(Exception):
    pass


class TTRApiDisabled(Exception):
    pass


def raise_on_error(r):
    j = json.loads(r.content)
    if int(j['status']) == 0:
        return

    error = j['content']['error']

    if error == 'NOT_LOGGED_IN':
        raise TTRNotLoggedIn

    if error == 'LOGIN_ERROR':
        raise TTRAuthFailure

    if error == 'API_DISABLED':
        raise TTRApiDisabled

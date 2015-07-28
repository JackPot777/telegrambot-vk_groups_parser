# -*- coding: utf-8 -*-
import requests
import re
import config
from time import time
from shelver import Shelver


RE_LOGIN_HASH = re.compile(r'name="lg_h" value="([a-z0-9]+)"')


class BadPasswordException(Exception):
    def __init__(self, function_name):
        super(BadPasswordException, self).__init__('{0} failed: Bad login or password'
                                                   .format(function_name))
        self.function_name = function_name


class CookieErrorException(Exception):
    def __init__(self, function_name):
        super(CookieErrorException, self) \
            .__init__('{0} failed: Cookies do not contain necessary element'
                      .format(function_name))
        self.function_name = function_name


def search_re(reg, string):
    """ Поиск по регулярке """
    s = reg.search(string)

    if s:
        groups = s.groups()
        return groups[0]


# TODO: Много разных проверок (капча, коды безопасности, таймауты...)
def get_new_token():
    storage = Shelver(config.database_file)
    method_name = 'auth.get_token'
    session = requests.Session()

    # Установим "правильный" юзер-агент
    session.headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 6.1; rv:38.0)'
                      'Gecko/20100101 Firefox/38.0'
    }

    # Мойте куки перед едой!
    session.cookies.clear()
    response = session.get('https://vk.com/')
    # TODO: Может быть, добавить сюда ещё и ip_h?
    params = {
        'act': 'login',
        'utf-8': 1,
        'email': config.username,
        'pass': config.password,
        'lg_h': search_re(RE_LOGIN_HASH, response.text),
    }
    response = session.post('https://login.vk.com/', params)
    if 'm=1' in response.url:
        raise BadPasswordException(method_name)

    data = {}

    if 'remixsid' in session.cookies:
        global remixsid
        remixsid = session.cookies['remixsid']
    else:
        raise CookieErrorException(method_name)

    if remixsid:
        data['remixdid'] = remixsid
    # Обновляем куки
    session.cookies.update({'p': session.cookies['p']})
    session.cookies.update({'l': session.cookies['l']})
    session.cookies.update({'remixsid': remixsid})

    values = {
        'client_id': config.client_id,
        'scope': config.permissions,
        'response_type': 'token',
    }
    response = session.post('https://oauth.vk.com/authorize', values)
    print(response.url)
    token = response.url.split('#')[1].split('=')[1].split('&')[0]
    expire_time = response.url.split('&')[1].split('=')[1]
    try:
        exp_time = int(time()) + int(expire_time)
        storage.save('token', token)
        storage.save('expire_time', exp_time)
        print('New token acquired!')
    except Exception as e:
        print('API::Auth::Saving data to db got exception: ' + str(e))

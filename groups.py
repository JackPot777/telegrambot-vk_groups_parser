# -*- coding: utf-8 -*-
import utils
import requests
import logging
from config import api_version, log_name

logger = logging.getLogger(log_name)


def get_post(group_id, offset):
    group_id = utils.shortname_to_id(group_id)
    params = {
        "gid": group_id,
        "access_token": utils.get_token(),
        "offset": offset,
        "v": api_version
    }
    result = requests.get('https://api.vk.com/method/execute.getWallPostNew', params=params)
    if 'error' in result.json()['response']:
        logger.error('Error in get_post()')
    return result.json()['response']


def get_unread_count(group_id, last_id):
    group_id = utils.shortname_to_id(group_id)
    params = {
        "gid": group_id,
        "access_token": utils.get_token(),
        "v": api_version
    }
    result = requests.get('https://api.vk.com/method/execute.getUnreadCount', params=params,
                          timeout=10)
    logger.debug('GetUnreadCount result: ' + str(result.json()))
    array = result.json()['response']
    chosen = 0
    logger.debug('UnreadCount last_id = ' + str(last_id))
    try:
        for index, item in enumerate(array['items']):
            if item > last_id:
                chosen += 1
            if item == last_id:
                break
    except TypeError as ex:
        logger.error('UnreadCount TypeError: {0!s}'.format(ex))
    logger.debug('UnreadCount chosen = {0!s}'.format(chosen))
    return chosen


def get_first_unread(group_id):
    group_id = utils.shortname_to_id(group_id)
    params = {
        "gid": group_id,
        "access_token": utils.get_token(),
        "v": api_version
    }
    result = requests.get('https://api.vk.com/method/execute.getUnreadCount', params=params)
    array = result.json()['response']
    if array['is_first_pinned'] is None:
        return None
    else:
        try:
            if array['is_first_pinned'] == 1:
                return array['items'][1]
            else:
                return array['items'][0]
        except TypeError as e:
            logger.error('FirstUnread TypeError: {0!s}'.format(e))
        except IndexError:
            logger.error('FirstUnread IndexError')
            pass


def get_first_post_id(group_id):
    """
    Получает идентификатор верхнего поста в группе.
    Если есть закрепленный пост, то возвращает первый на самой стене
    :param group_id: ID группы (буквенный или числовой)
    """
    group_id = utils.shortname_to_id(group_id)
    params = {
        "gid": group_id,
        "access_token": utils.get_token(),
        "v": api_version
    }
    result = requests.get('https://api.vk.com/method/execute.getFirstPostId', params=params)
    try:
        res = result.json()['response']
        return res
    except Exception as e:
        logger.error('get_first_post_id exception: {0!s}'.format(e))
        return None


def update_ids(list_of_groups):
    from shelver import Shelver
    from config import database_file
    storage = Shelver(database_file)
    for group in list_of_groups:
        import time
        time.sleep(1)
        try:
            last_id = get_first_post_id(group)
            # Если это первый запуск, то сохраняем первое же значение
            storage.get_with_create(group, last_id)
        except Exception as ex:
            logger.error('UpdateIDS failed: {0!s}'.format(ex))


def get_group_name_by_id(group_id):
    group_id = utils.shortname_to_id(group_id)
    params = {"gid": group_id,
              "access_token": utils.get_token()
              }
    result = requests.get('https://api.vk.com/method/execute.getGroupNameById', params=params)
    if 'error' not in result.json():
        return result.json()['response']
    else:
        return None


def is_first_pinned(group_id):
    group_id = utils.shortname_to_id(group_id)
    params = {
        "owner_id": -group_id,
        "count": 2,
        "access_token": utils.get_token()
    }
    result = requests.get('https://api.vk.com/method/wall.get', params=params)
    try:
        v = result.json()['response'][1]['is_pinned']
        return True
    except Exception:
        return False


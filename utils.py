# -*- coding: utf-8 -*-
import requests
import config
import os
import time
import logging
from shelver import Shelver


logger = logging.getLogger(config.log_name)

class NoSuchShortnameException(Exception):
    def __init__(self, method_name, result):
        super().__init__('{0} failed. Returned result: {1}'.format(method_name, result))
        self.function_name = method_name
        self.result = result


# Токен валиден сутки, проверяем
def is_token_valid():
    storage = Shelver(config.database_file)
    cur_time = storage.get_with_create('expire_time', 0)
    if int(time.time()) < int(cur_time):
        return True
    elif int(time.time()) > int(cur_time):
        logger.info('Token expired. Need to get new one')
        return False


def shortname_to_id(shortname):
    """
    Универсальный метод, возвращает числовой ID для переданной строки
    :param shortname:
    :return:
    """
    method_name = 'utils::shortname_to_id'
    if isinstance(shortname, int):
        return shortname

    data = dict(
        screen_name=shortname
    )

    result = requests.get('https://api.vk.com/method/utils.resolveScreenName', params=data)
    js = result.json()
    if len(str(js)) < 17:
        raise NoSuchShortnameException(method_name, js)
    try:
        uid = js['response']['object_id']
        return uid
    except TypeError as te:
        logger.error('shortname_to_id Exception: ' + str(te))


def get_token():
    """
    Получает токен из локального хранилища
    :return: (str) значение токена
    """
    # Небольшой хак, чтобы хранилище всегда было в корне проекта
    storage = Shelver(os.path.join(os.path.dirname(__file__), config.database_file))
    return storage.get('token')


# Получаем список юзеров, подписавшихся на обновления в конкретной категории
def get_list_of_users_in_category(list_name):
    storage = Shelver(config.database_file)
    return list(storage.get_with_create(list_name + config.users_db_postfix, []))


def add_user_to_list_of_subscribers(chat_id, list_name):
    storage = Shelver(config.database_file)
    return storage.append(list_name + config.users_db_postfix, chat_id)


# Убираем юзера из списка
def delete_user_from_list_of_subscribers(chat_id, list_name):
    storage = Shelver(config.database_file)
    return storage.remove(list_name + config.users_db_postfix, chat_id)


# Скачивам файл (украл из инета)
def download_file(url, folder):
    """
    Скачивает файл в указанный каталог
    :param url: Ссылка для загрузки
    :param folder: Каталог для загрузки
    :return: Имя файла (без указания каталога)
    """
    r = requests.get(url, stream=True)
    local_filename = folder + os.path.sep + url.split('/')[-1]
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
    return local_filename


def string_splitter(line, chars_in_each_line):
    """
    Делит длинную строку на несколько помельче
    :param line: Строка, которую необходимо поделить
    :param chars_in_each_line: Количество символов в каждом куске
    :return: Массив подстрок
    """
    return [line[i:i + chars_in_each_line] for i in range(0, len(line), chars_in_each_line)]


def get_list_of_groups_in_category(category_name):
    storage = Shelver(config.database_file)
    return storage.get(category_name.strip())


def init_logger():
    global logger
    logger = logging.getLogger(config.log_name)
    logging.basicConfig(filename=config.log_name + '.log',
                        format='[%(asctime)s] %(filename)s:%(lineno)d %(levelname)s - %(message)s',
                        datefmt='%d.%m.%Y %H:%M:%S')
    if config.log_level:
        if config.log_level.lower() == 'debug':
            logger.setLevel(logging.DEBUG)
        elif config.log_level.lower() == 'info':
            logger.setLevel(logging.INFO)
        elif config.log_level.lower() == 'warn' or config.log_level.lower() == 'warning':
            logger.setLevel(logging.WARNING)
        elif config.log_level.lower() == 'error':
            logger.setLevel(logging.ERROR)
        else:
            logger.setLevel(logging.WARNING)
    else:
        logger.setLevel(logging.WARNING)



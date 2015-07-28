#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
import config
import telebot
import time
import groups
import utils
import auth
import parsers
import logging
import sys
import signal
from telebot import types
from shelver import Shelver

# Временные списки, чтобы отслеживать сообщения о подписке/отписке
list_users_to_subscribe = []
list_users_to_unsibscribe = []
logger = logging.getLogger(config.log_name)

# Обработчик KeyboardInterrupt
def signal_handler(signal, frame):
    logger.info('Signal catched, closing DB')
    print('Signal catched, closing DB')
    Shelver(config.database_file).close()
    sys.exit(0)


# Функция, работающая в цикле
def send_message_with_hide_keyboard(chat_id, text, hide_keyboard=False):
    message_length = 2000
    if hide_keyboard:
        keyboard = types.ReplyKeyboardHide()
    else:
        keyboard = None
    for msg_part in utils.string_splitter(text, message_length):
        tb.send_message(chat_id, msg_part, disable_web_page_preview=True, reply_markup=keyboard)


def cycle(m_categories, storage):
    print('----- CYCLE START -----')
    # print(m_groups.split(','))
    for current_category in m_categories.split(','):
        logger.debug('Category Started: {0}'.format(str(current_category)))
        list_of_groups = utils.get_list_of_groups_in_category(current_category.lstrip())
        # Получаем список юзеров, подписавшихся на обновления
        users = utils.get_list_of_users_in_category(current_category.strip())
        for group_id in list_of_groups:
            # Если на категорию никто не подписан, обновляет записи о постах и не продолжаем
            if len(users) < 1:
                logger.debug('No users in category {0}. Skipping...'.format(str(current_category)))
                groups.update_ids(list_of_groups)
                # print('Groups updated!')
                break
            logger.debug('Group start: {0!s}'.format(group_id))
            last_id = groups.get_first_post_id(group_id)
            if last_id is None or 0:
                logger.warning('Last ID is None or Zero, skipping group for now...')
                continue
            time.sleep(1)
            # Если это первый запуск, то сохраняем первое же значение
            last_saved_id = shelver.get_with_create(group_id, last_id)

            # Чтобы ВК не забанил, сделаем паузу
            time.sleep(1)
            try:
                unread_count = groups.get_unread_count(group_id, last_saved_id)
            except Exception:
                logger.warning('Could not get unread_count. Skipping...')
                continue
            global offset
            # Тернарный оператор
            offset = 1 if groups.is_first_pinned(group_id) else 0
            for i in range(unread_count):
                # Получаем сам пост.
                wall_post = groups.get_post(group_id, offset)
                logger.debug('Offset = {0!s}'.format(offset))
                offset += 1
                # Если есть текст, то отправляем его всем юзерам
                if len(wall_post['text']) > 0:
                    for user in users:
                        send_message_with_hide_keyboard(user,
                                                        'Запись из группы\"{0}\":\n{1}'.format(
                                                            groups.get_group_name_by_id(group_id),
                                                            wall_post['text']))
                else:
                    for user in users:
                        tb.send_message(user, 'Запись из группы \"{0}\"'
                                        .format(groups.get_group_name_by_id(group_id)))
                # Пробегаем по аттачам
                if wall_post['items']:
                    for attachment in wall_post['items']:
                        # Фотография
                        if attachment['type'] == 'photo':
                            parsers.parse_photo(attachment, users, tb)
                        if attachment['type'] == 'video':
                            parsers.parse_video(attachment, users, tb)
                        if attachment['type'] == 'audio':
                            parsers.parse_audio(attachment, users, tb)
                        if attachment['type'] == 'link':
                            parsers.parse_link(attachment, users, tb)
                        time.sleep(1)
                    time.sleep(3)
            # Сохраняем новое значение верхнего поста в БД
            storage.save(group_id, last_id)
    print('----- CYCLE END   -----')


# TODO: ПЕРЕПИСАТЬ КЛАВИАТУРУ, ONE_TIME РАБОТАЕТ ПО-ДРУГОМУ!!!
def choose_groups(chat_id, to_add):
    """
    Предлагает юзеру выбрать группы для подписки/отписки
    :param chat_id: ID юзера
    :param to_add: Если True, то диалог добавления, если False - удаления
    """
    storage = Shelver(config.database_file)
    global list_of_buttons
    list_of_usergroups = storage.find_all('.*_users')
    list_of_buttons = [elem[:-6] for elem in list_of_usergroups]
    markup = types.ReplyKeyboardMarkup()
    # Позволяем ресайзить клаву
    markup.resize_keyboard = True
    # Если добавляем
    if to_add:
        for i in range(len(list_of_buttons)):
            if chat_id not in storage.get(list_of_usergroups[i]):
                markup.row('/{0}:+{1}'.format('group' + str(i), list_of_buttons[i]))
        markup.row('/0:Закрыть')
        tb.send_message(chat_id, 'Выберите нужные категории. Как закончите - нажмите "Закрыть"',
                        reply_markup=markup)
        list_users_to_subscribe.append(chat_id)
    if not to_add:
        for i in range(len(list_of_buttons)):
            if chat_id in storage.get(list_of_usergroups[i]):
                markup.row('/{0}:-{1}'.format('group' + str(i), list_of_buttons[i]))
        markup.row('/0:Закрыть')
        tb.send_message(chat_id, 'Выберите нужные категории. Как закончите - нажмите "Закрыть"',
                        reply_markup=markup)
        list_users_to_unsibscribe.append(chat_id)


# Прослушивает список новых сообщений
def listener(messages):
    for m in messages:
        if m.content_type == 'text' and m.text == '/subscribe':
            choose_groups(m.chat.id, True)
        if m.content_type == 'text' and m.text == '/unsubscribe':
            choose_groups(m.chat.id, False)
        if m.text.startswith('/group'):
            if '+' in m.text and m.chat.id in list_users_to_subscribe:
                utils.add_user_to_list_of_subscribers(m.chat.id,
                                                      m.text[m.text.find(':') + 2:].strip())
                # list_users_to_subscribe.remove(m.chat.id)
                send_message_with_hide_keyboard(m.chat.id, 'Вы подписались на категорию '
                                                + m.text[m.text.find(':') + 2:].strip())
            if '-' in m.text and m.chat.id in list_users_to_unsibscribe:
                utils.delete_user_from_list_of_subscribers(m.chat.id,
                                                           m.text[m.text.find(':') + 2:].strip())
                # list_users_to_unsibscribe.remove(m.chat.id)
                send_message_with_hide_keyboard(m.chat.id, 'Вы отписались от категории '
                                                + m.text[m.text.find(':') + 2:].strip())
        if m.text == '/0:Закрыть':
            hider = types.ReplyKeyboardHide()
            tb.send_message(m.chat.id, 'Готово!', reply_markup=hider)
            try:
                list_users_to_unsibscribe.remove(m.chat.id)
                list_users_to_subscribe.remove(m.chat.id)
            except:
                pass


# Запускаем бота
tb = telebot.TeleBot(config.token)
tb.set_update_listener(listener)
# Запускаем логгер
utils.init_logger()
tb.polling(none_stop=True, interval=4)
shelver = Shelver(config.database_file)
# Ловим сигнал прерывания
signal.signal(signal.SIGINT, signal_handler)
# В цикле запускается анализ страниц, рекомендую сделать Sleep хотя бы 2 минуты (120)
while True:
    if not utils.is_token_valid():
        auth.get_new_token()
    cycle(config.categories, shelver)
    time.sleep(config.SCANNING_INTERVAL)
    pass

# -*- coding: utf-8 -*-
import utils
import os
import config
import logging

logger = logging.getLogger(config.log_name)


def parse_photo(js, userlist, bot):
    logger.debug('Parse photo start')
    global photo_file_id
    try:
        url = js['photo']['photo_604']
    # Если картинка меньше 604 по бОльшей стороне - нахер такая нужна?
    except Exception as e:
        logger.error('Getting photo_604 failed: {0!s}'.format(e))
        return
    downloaded_file = utils.download_file(url, 'imgs')
    for j in range(len(userlist)):
        if j == 0:
            ph = open(downloaded_file, 'rb')
            logger.debug('Sending by file...')
            photo_links = bot.send_photo(userlist[j], ph).photo
            try:
                photo_file_id = photo_links[len(photo_links) - 1].file_id
            except Exception as e:
                logger.warning('Could not get file_id: {0!s}'.format(e))
                return
            finally:
                ph.close()
        else:
            logger.debug('Sending by id...')
            bot.send_photo(userlist[j], photo_file_id)
    # Удаляем фото, если не нужно
    if not config.store_photo:
        try:
            os.remove(downloaded_file)
        except Exception as ex:
            print('{0}: {1}'.format(type(ex).__name__, str(ex)))
    logger.debug('Parse photo end')


def parse_video(js, userlist, bot):
    logger.debug('Parse video start')
    for user in userlist:
        bot.send_message(user,
                         'Видео \"{0}\": https://vk.com/video{1}_{2}?access_key={3}'
                         .format(js['video']['title'],
                                 js['video']['owner_id'],
                                 js['video']['id'],
                                 js['video']['access_key']))
    logger.debug('Parse video end')


def parse_audio(js, userlist, bot):
    logger.debug('Parse audio start')
    global audio_file_id
    try:
        downloaded_file = utils.download_file(js['audio']['url'].split('?')[0], 'music')
    except Exception as e:
        logger.error('Could not download audio: {0!s}'.format(e))
        return
    for j in range(len(userlist)):
        if j == 0:
            m_music = open(downloaded_file, 'rb')
            logger.debug('Sending audio by file...')
            audio_file_id = bot.send_document(userlist[j], m_music).document.file_id
            m_music.close()
        else:
            logger.debug('Sending audio by id...')
            bot.send_document(userlist[j], audio_file_id)
    # Удаляем аудио, если не нужно
    if not config.store_audio:
        try:
            os.remove(downloaded_file)
        except Exception as ex:
            print('{0}: {1}'.format(type(ex).__name__, str(ex)))
    logger.debug('Parse audio end')


def parse_link(js, userlist, bot):
    logger.debug('Parse link started')
    try:
        for user in userlist:
            bot.send_message(user, js['link']['url'])
    except Exception as ex:
        logger.error('{0}: {1}'.format(type(ex).__name__, str(ex)))
        print('{0}: {1}'.format(type(ex).__name__, str(ex)))
    logger.debug('Parse link finished')
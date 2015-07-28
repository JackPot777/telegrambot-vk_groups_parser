# -*- coding: utf-8 -*-

##########################
# Учётная запись и токен #
##########################
token = 'TOKEN'
SCANNING_INTERVAL = 300  # Интервал сканирования страниц (в секундах)
'''
+8192 - Доступ к обычным и расширенным методам работы со стеной
+262144 - Доступ к группам пользователя.
'''
permissions = 270336
username = 'username'
password = 'password'
client_id = 1234567 # APP_ID созданного приложения
database_file = 'storage'  # Название хранилища
api_version = '5.34'  # Версия API VK


###########################
# Основные настройки бота #
###########################
# Постфикс, используемый в "ключах" для юзеров
users_db_postfix = '_users'
# Категории и названия групп внутри категорий
categories = 'News,Music,Games,Sport'
cat_entries = 'oldlentach,lentaru\n' \
              'musicwarehouse,electronicmelody\n' \
              'onlinegamer,shazoo\n' \
              'sportbox,sportexpress'

              
#######################
#  Cохранение данных  #
#######################
send_photo = True  # Скачивать ли фото?
store_photo = False  # Сохранять фото или удалять с сервера после отправки всем?
send_audio = False  # Аналогично для аудио
store_audio = False  # Не имеет смысла, если send_audio = False, но всё же


#######################
# Логирование событий #
#######################
log_name = 'vk-group-parser'
# По обширности: DEBUG > INFO > WARNING > ERROR
log_level = 'warning'
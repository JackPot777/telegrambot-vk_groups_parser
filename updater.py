# -*- coding: utf-8 -*-
"""
При изменении списка групп, необходимо запустить этот файл
"""

from shelver import Shelver
from config import database_file, categories, cat_entries


list_categories = categories.split(',')
list_entries = cat_entries.split('\n')
storage = Shelver(database_file)
if len(list_categories) != len(list_entries):
    print('Размерности массивов не совпадают! Проверьте списки.')
else:
    for i in range(len(list_categories)):
        for j in range(len(list_entries[i].split(','))):
            print('Inserting {0} into {1}'.format(list_entries[i].split(',')[j], list_categories[i]))
            storage.append(list_categories[i], list_entries[i].split(',')[j].strip(), strict=False)

print(len(storage.get('Новости')[1]))





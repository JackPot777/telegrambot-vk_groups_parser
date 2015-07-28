#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

from shelver import Shelver
import shelve
import config

storage = Shelver(config.database_file)
print(config.categories)
for entry in config.categories.split(','):
    storage.save(entry.strip(), [])
    storage.save(entry.strip() + config.users_db_postfix, [])

    
list_categories = config.categories.split(',')
list_entries = config.cat_entries.split('\n')
if len(list_categories) != len(list_entries):
    print('Размерности массивов не совпадают! Проверьте списки.')
else:
    for i in range(len(list_categories)):
        for j in range(len(list_entries[i].split(','))):
            print('Inserting {0} into {1}'.format(list_entries[i].split(',')[j], list_categories[i]))
            storage.append(list_categories[i], list_entries[i].split(',')[j].strip(), strict=True)

print(len(storage.get('News')[1]))


storage.save('expire_time', 0)
storage.save('token', 0)
storage.close()

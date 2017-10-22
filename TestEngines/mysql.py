#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pymysql.cursors
from TestEngines.config import *


class Test:
    def __init__(self):
        self.connection = pymysql.connect(
            host=CONFIG.get('MYSQL', 'HOST'),
            port=int(CONFIG.get('MYSQL', 'PORT')),
            user=CONFIG.get('MYSQL', 'USERNAME'),
            password=CONFIG.get('MYSQL', 'PASSWORD'),
            db=CONFIG.get('MYSQL', 'DATABASE'),
            charset=CONFIG.get('MYSQL', 'CHARSET'),
            cursorclass=pymysql.cursors.DictCursor
        )

    def action(self, action_value, action, *action_sub):
        with self.connection.cursor() as cursor:
            if not action_value:
                raise ValueError('This action need a value.')
            cursor.execute(action_value)
            if action == 'commit':
                return self.connection.commit()
            elif action == 'fetchall':
                return cursor.fetchall()
            elif action == 'fetchmany':
                if action_sub:
                    number = int(action_sub[0])
                else:
                    number = int(CONFIG.get('MYSQL', 'FETCH_NUM'))
                return cursor.fetchmany(number)
            elif action == 'fetchone':
                result = cursor.fetchone()
                if action_sub:
                    result = result[action_sub[0]]
                return result
            elif action == 'sql':
                with open(os.path.join(FILE_DIR, action_value), 'r') as f:
                    for line in filter(lambda x: x.strip(),f):
                        cursor.execute(line)
                return self.connection.commit()

    def clean(self):
        self.connection.close()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pymysql.cursors
from Engines.config import *


class Test:
    def __init__(self):
        self.connection = pymysql.connect(host=CONFIG.get('MYSQL', 'HOST'),
                                          port=int(CONFIG.get('MYSQL', 'PORT')),
                                          user=CONFIG.get('MYSQL', 'USERNAME'),
                                          password=CONFIG.get('MYSQL', 'PASSWORD'),
                                          db=CONFIG.get('MYSQL', 'DATABASE'),
                                          charset=CONFIG.get('MYSQL', 'CHARSET'),
                                          cursorclass=pymysql.cursors.DictCursor)

    def action(self, action_value, action, *action_sub):
        with self.connection.cursor() as cursor:
            if not action_value:
                raise ValueError('This action need a value.')
            cursor.execute(action_value)
            if action == 'commit':
                self.connection.commit()
            elif action == 'fetchall':
                return cursor.fetchall()
            elif action == 'fetchmany':
                return cursor.fetchmany(int(action_sub[0]))
            elif action == 'fetchone':
                result = cursor.fetchone()
                if len(action_sub) == 2:
                    result = result[action_sub[1]]
                return result

    def clean(self):
        self.connection.close()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pymysql.cursors
from Engines.config import *
import logging


class Test:
    def __init__(self):
        self.connection = pymysql.connect(host=CONFIG.get('MYSQL', 'HOST'),
                                          port=int(CONFIG.get('MYSQL', 'PORT')),
                                          user=CONFIG.get('MYSQL', 'USERNAME'),
                                          password=CONFIG.get('MYSQL', 'PASSWORD'),
                                          db=CONFIG.get('MYSQL', 'DATABASE'),
                                          charset=CONFIG.get('MYSQL', 'CHARSET'),
                                          cursorclass=pymysql.cursors.DictCursor)

    def action(self, action, action_value):
        with self.connection.cursor() as cursor:
            if not action_value:
                raise ValueError('This action need a value.')
            cursor.execute(action_value)
            if action == 'commit':
                self.connection.commit()
            elif action == 'fetchone':
                return cursor.fetchone()
            elif action == 'fetchall':
                return cursor.fetchall()
            elif action.split('.')[0] == 'fetchmany':
                return cursor.fetchmany(int(action.split('.')[-1]))

    def clean(self):
        self.connection.close()

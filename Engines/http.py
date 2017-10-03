#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
from urllib.parse import urljoin
from Engines.config import *


class Test:
    def __init__(self):
        self.kw = {}
        self.kw_dict = {}
        self.kw_temp = None
        self.locator('timeout', CONFIG.get('HTTP', 'TIMEOUT'))

    # encapsulate params
    def locator(self, key, value, *args):
        del args
        if key in ('<headers>', '<params>'):
            self.kw_temp = self.kw
            self.kw = {}
        elif key == '</headers>':
            self.kw_dict['headers'] = self.kw
            self.kw = self.kw_temp
        elif key == '</params>':
            self.kw_dict['params'] = self.kw
            self.kw = self.kw_temp
        else:
            if key == "timeout":
                value = float(value)
            elif key in ('headers', 'params'):
                value = eval(value)
            elif value.title() in ('True', 'False'):
                value = {'True': True, 'False': False}[key]
            self.kw[key] = value

    @staticmethod
    def locator_log(locator, locator_value, action, action_value):
        return locator + (' = ' if locator_value else '') + locator_value

    def action(self, action_value, action):
        if '://' not in action_value:
            action_value = urljoin(CONFIG.get('HTTP', 'BASEURL'), action_value)
        r = getattr(requests, action)(action_value, **self.kw, **self.kw_dict)
        self.kw = {}
        return r

    def clean(self):
        pass

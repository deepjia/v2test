#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import requests
from ast import literal_eval
from urllib.parse import urljoin
from TestEngines.config import *


class Test:
    def __init__(self):
        self.tag = 'parameters'
        self.father_tag = None
        self.parameters = {}
        # set default timeout parameter
        self.locator('timeout', CONFIG.get('HTTP', 'TIMEOUT'))

    # encapsulate params
    def locator(self, key, value, *args):
        del args
        # open dict (headers, params etc.)
        if key.endswith('{'):
            self.father_tag = self.tag
            self.tag = key.rstrip('{')
            logging.info("self.tag:"+self.tag)
            setattr(self, self.tag, {})

        # open list (data etc.)
        elif key.endswith('['):
            self.tag = key.rstrip('[')
            setattr(self, self.tag, [])

        # close dict/list
        elif key == '}' or key == ']':
            getattr(self, self.father_tag)[self.tag] = getattr(self, self.tag)
            setattr(self, self.tag, None)
            self.tag = self.father_tag

        # parameters encapsulate
        elif key == 'files{}':
            getattr(self, self.tag)[key] = {'file': open(value, 'rb')}

        # list as parameter
        elif isinstance(getattr(self, self.tag), list):
            getattr(self, self.tag).append((key, literal_eval(value)))
        # dict as parameter
        elif isinstance(getattr(self, self.tag), dict):
            getattr(self, self.tag)[key] = literal_eval(value)

    @staticmethod
    def locator_log(locator, locator_value, *action_and_value):
        # Do not log action_and_value for this engine
        del action_and_value
        return locator + (' = ' if locator_value else '') + locator_value

    def action(self, action_value, action):
        # for relative path, join with base url
        if '://' not in action_value:
            action_value = urljoin(
                CONFIG.get('HTTP', 'BASEURL'), action_value)
        r = getattr(requests, action)(action_value, **self.parameters)
        # Clear parameters
        self.parameters = {}
        return r

    @staticmethod
    def check(response, arg, *args):
        if arg == 'json':
            r = response.json()
            # extract from list/dict
            for index in args:
                index = int(index) if isinstance(r, list) else index
                r = r[index]
            return r
        else:
            return getattr(response, arg)

    @staticmethod
    def clean():
        pass

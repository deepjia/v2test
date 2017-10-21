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
        #self.headers = self.params = self.data = None
        self.locator('timeout', CONFIG.get('HTTP', 'TIMEOUT'))

    # encapsulate params
    def locator(self, key, value, *args):
        del args
        # open
        # headers,params or else
        if key.endswith('{'):
            self.father_tag = self.tag
            self.tag = key.rstrip('{')
            logging.info("self.tag:"+self.tag)
            setattr(self, self.tag, {})

        # data or else
        elif key.endswith('['):
            self.tag = key.rstrip('[')
            setattr(self, self.tag, [])

        # close
        elif key == '}' or key == ']':
            getattr(self, self.father_tag)[self.tag] = getattr(self, self.tag)
            setattr(self, self.tag, None)
            self.tag = self.father_tag

        # parameters encapsulate
        elif key == 'files{}':
            getattr(self, self.tag)[key] = {'file': open(value, 'rb')}

        elif isinstance(getattr(self, self.tag), list):
            getattr(self, self.tag).append((key, literal_eval(value)))

        elif isinstance(getattr(self, self.tag), dict):
            getattr(self, self.tag)[key] = literal_eval(value)

    @staticmethod
    def locator_log(locator, locator_value, *action_and_value):
        # Do not log action_and_value for this engine
        del action_and_value
        return locator + (' = ' if locator_value else '') + locator_value

    def action(self, action_value, action):
        if '://' not in action_value:
            action_value = urljoin(
                CONFIG.get('HTTP', 'BASEURL'), action_value)
        r = getattr(requests, action)(action_value, **self.parameters)
        # self.parameters = {}
        return r

    @staticmethod
    def check(response, arg, *args):
        if arg == 'json':
            r = response.json()
            for i in args:
                i = int(i) if isinstance(r, list) else i
                r = r[i]
        else:
            r = getattr(response, arg)
        return r

    @staticmethod
    def clean():
        pass

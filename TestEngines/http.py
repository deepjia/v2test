#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
from ast import literal_eval
from urllib.parse import urljoin
from TestEngines.config import *


class Test:
    def __init__(self):
        self.parameters = {}
        self.headers = self.params = self.data = None
        self.locator('timeout', CONFIG.get('HTTP', 'TIMEOUT'))

    # encapsulate params
    def locator(self, key, value, *args):
        del args
        # open
        if key == '<headers>':
            self.headers = {}
        elif key == '<params>':
            self.params = {}
        elif key == '<data>':
            self.data = []
        # close
        elif key == '</headers>':
            self.parameters['headers'] = self.headers
            self.headers = None
        elif key == '</params>':
            self.parameters['params'] = self.params
            self.params = None
        elif key == '</data>':
            self.parameters['data'] = self.data
            self.data = None
        # encapsulate
        elif self.data is not None:
            self.data.append((key, literal_eval(value)))
        elif self.headers is not None:
            self.headers[key] = literal_eval(value)
        elif self.params is not None:
            self.params[key] = literal_eval(value)
        # parameters
        elif key == 'files':
            self.parameters['files'] = {'file': open(value, 'rb')}
        else:
            self.parameters[key] = literal_eval(value)

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

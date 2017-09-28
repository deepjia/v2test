#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
from Engines.config import *


class Test:
    def __init__(self):
        self.kw = {}
        self.kw_dict = {}

    # encapsulate params
    def locator(self, key, value):
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

    def get(self, url):
        return self.action("get", url)

    def post(self, url):
        return self.action("post", url)

    def head(self, url):
        return self.action("head", url)

    def put(self, url):
        return self.action("put", url)

    def delete(self, url):
        return self.action("delete", url)

    def options(self, url):
        return self.action("options", url)

    # all requests
    def action(self, action, url):
        if url == '':
            url = CONFIG.get('HTTP', 'URL')
        r = getattr(requests, action)(url, **self.kw, **self.kw_dict)
        self.kw = {}
        return r

    def clean(self):
        pass

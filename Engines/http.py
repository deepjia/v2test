#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests


class Test:
    def __init__(self):
        self.kw = {}

    # encapsulate params
    def locate(self, key, value):
        if key or value:
            self.kw[key] = value
        return self

    # get
    def get(self, url):
        r = requests.get(url, **self.kw)
        self.kw = {}
        return r

    def post(self, url):
        r = requests.post(url, **self.kw)
        self.kw = {}
        return r

    def head(self, url):
        r = requests.head(url, **self.kw)
        self.kw = {}
        return r

    def put(self, url):
        r = requests.put(url, **self.kw)
        self.kw = {}
        return r

    def delete(self, url):
        r = requests.delete(url, **self.kw)
        self.kw = {}
        return r

    def options(self, url):
        r = requests.options(url, **self.kw)
        self.kw = {}
        return r

    # all requests
    def request(self, action, url):
        r = getattr(requests, action)(url, **self.kw)
        self.kw = {}
        return r

    def clean(self):
        pass

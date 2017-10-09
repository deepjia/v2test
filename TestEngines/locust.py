#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import subprocess
from datetime import datetime
from TestEngines.config import *


class Test:
    def __init__(self):
        self.args = {}
        for k in ('client','rate','number','host'):
            self.args[k] = CONFIG.get('LOCUST', k.upper())

    # encapsulate params
    def locator(self, key, value, *args):
        del args
        if key in ('client', 'rate', 'number', 'host'):
            self.args[key] = value

    def action(self, action_value, action):
        if action == 'file':
            path = ['locust', '-f', os.path.join(FILE_DIR, action_value), '--no-web',
                    datetime.now().strftime("--csv=TestReports/Test_Locust_%Y-%m-%d_%H-%M-%S")]
            for k, w in self.args.items():
                if w:
                    path.extend(({'client': '-c', 'rate': '-r', 'number': '-n', 'host': '-H'}[k], w))
        else:
            raise ValueError('Invalid Action.')
        r = subprocess.run(path, check=True, stdout=subprocess.PIPE)
        return r.stdout.decode('utf-8')

    @staticmethod
    def locator_log(locator, locator_value, action, action_value):
        return locator + (' = ' if locator_value else '') + locator_value

    @staticmethod
    def clean():
        pass

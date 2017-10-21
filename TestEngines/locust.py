#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
from datetime import datetime
from TestEngines.config import *


class Test:
    def __init__(self):
        self.args = {}
        for k in ('client', 'rate', 'number', 'host'):
            self.args[k] = CONFIG.get('LOCUST', k.upper())

    # encapsulate params
    def locator(self, key, value, *args):
        del args
        if key in ('client', 'rate', 'number', 'host'):
            self.args[key] = value

    def action(self, action_value, action):
        # run locust python script
        if action == 'file':
            name_prefix = os.path.join('TestReports', 'Test_Locust_')
            name_suffix = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            path = os.path.join(FILE_DIR, action_value)
            cmd = ['locust', '-f', path, '--no-web',
                   "--csv=" + name_prefix + name_suffix]
            for k, w in self.args.items():
                cmd.append({'rate': '-r',
                            'host': '-H',
                            'number': '-n',
                            'client': '-c'}[k])
                cmd.extend((k,w))
                cmd.append(w)
        else:
            raise ValueError('Invalid Action.')
        # background or not
        if CONFIG.get('LOCUST', 'BACKGROUND') == 'Y':
            r = subprocess.run(cmd, check=True, stdout=subprocess.PIPE)
            return r.stdout.decode('utf-8')
        else:
            subprocess.Popen(cmd)

    @staticmethod
    def locator_log(locator, locator_value, *action_and_value):
        # Do not log action_and_value for this engine
        del action_and_value
        return locator + (' = ' if locator_value else '') + locator_value

    @staticmethod
    def clean():
        pass

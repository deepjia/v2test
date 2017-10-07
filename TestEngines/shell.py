#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import subprocess
from TestEngines.config import *


class Test:
    def __init__(self):
        pass

    @staticmethod
    def action(action_value, action):
        if action =='python':
            path = CONFIG.get('SHELL','PYTHON')
            path = path if path else sys.executable
            action_value = [path, os.path.join(FILE_DIR, action_value)]
        elif action =='bash':
            path = CONFIG.get('SHELL', 'BASH')
            path = path if path else '/usr/bin/bash'
            action_value = [path, os.path.join(FILE_DIR, action_value)]
        elif action == 'ruby':
            path = CONFIG.get('SHELL', 'RUBY')
            path = path if path else '/usr/bin/ruby'
            action_value = [path, os.path.join(FILE_DIR, action_value)]
        elif action == 'perl':
            path = CONFIG.get('SHELL', 'PERL')
            path = path if path else '/usr/bin/perl'
            action_value = [path, os.path.join(FILE_DIR, action_value)]
        elif action == 'file':
            action_value = os.path.join(FILE_DIR, action_value)
        elif action != 'command':
            raise ValueError('Invalid Action.')
        r = subprocess.run(action_value, shell=True, check=True, stdout=subprocess.PIPE)
        return r.stdout.decode('utf-8')

    @staticmethod
    def clean():
        pass

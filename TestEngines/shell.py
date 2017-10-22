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
        shell = None
        if action =='python':
            path = CONFIG.get('SHELL','PYTHON')
            path = path if path else sys.executable
            path = path.split()
            path.append(os.path.join(FILE_DIR, action_value))
        elif action =='bash':
            path = CONFIG.get('SHELL', 'BASH')
            path = path if path else '/usr/bin/bash'
            path = path.split()
            path.append(os.path.join(FILE_DIR, action_value))
        elif action == 'ruby':
            path = CONFIG.get('SHELL', 'RUBY')
            path = path if path else '/usr/bin/ruby'
            path = path.split()
            path.append(os.path.join(FILE_DIR, action_value))
        elif action == 'perl':
            path = CONFIG.get('SHELL', 'PERL')
            path = path if path else '/usr/bin/perl'
            path = path.split()
            path.append(os.path.join(FILE_DIR, action_value))
        elif action == 'file':
            path = os.path.join(FILE_DIR, action_value)
            shell = True
        elif action == 'command':
            path = action_value
            shell = True
        else:
            raise ValueError('Invalid Action.')
        r = subprocess.run(
            path, shell=shell, check=True, stdout=subprocess.PIPE
        )
        return r.stdout.decode('utf-8')

    @staticmethod
    def clean():
        pass

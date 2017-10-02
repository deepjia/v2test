#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
from Engines.config import *


class Test:
    def __init__(self):
        pass

    @staticmethod
    def action(action, action_value):
        if action == 'file':
            action_value = os.path.join(FILE_DIR, action_value)
        r = subprocess.run(action_value, shell=True, check=True, stdout=subprocess.PIPE)
        return r.stdout.decode('utf-8')

    @staticmethod
    def clean():
        pass

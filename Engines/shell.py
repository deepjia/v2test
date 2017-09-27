#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import subprocess
from Engines.config import *


class Test:
    def __init__(self):
        pass

    # all requests
    def cmd(self, command):
        r = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE)
        return r.stdout.decode('utf-8')

    def file(self, filename):
        filename = os.path.join(FILE_DIR,filename)
        r = subprocess.run(filename, shell=True, check=True, stdout=subprocess.PIPE)
        return r.stdout.decode('utf-8')

    def clean(self):
        pass

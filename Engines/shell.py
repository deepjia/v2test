#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
from Engines.config import *


class Test:
    def __init__(self):
        pass

    @staticmethod
    def cmd(command):
        r = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE)
        return r.stdout.decode('utf-8')

    @staticmethod
    def file(filename):
        filename = os.path.join(FILE_DIR, filename)
        r = subprocess.run(filename, shell=True, check=True, stdout=subprocess.PIPE)
        return r.stdout.decode('utf-8')

    @staticmethod
    def clean():
        pass

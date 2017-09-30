#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import configparser


class GetConfig:
    def __init__(self, file):
        self.config = configparser.ConfigParser()
        self.config.read(file)

    def get(self, section, key):
        return self.config[section][key]


DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
CONFIG_FILE = os.path.join(DIR, 'config.ini')
CASE_DIR = os.path.join(DIR, 'Cases')
FILE_DIR = os.path.join(DIR, 'Files')
REPORT_DIR = os.path.join(DIR, 'Reports')
ENGINE_DIR = os.path.join(DIR, 'Engines')
CASE_TEMP_DIR = os.path.join(ENGINE_DIR, 'temp')
CASE_FILES = [x.path for x in os.scandir(CASE_DIR) if x.is_file() and x.name.endswith(".xlsx") and '~$' not in x.name]

CONFIG = GetConfig(CONFIG_FILE)

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
CASE_DIR = os.path.join(DIR, 'TestCases')
FILE_DIR = os.path.join(DIR, 'TestFiles')
REPORT_DIR = os.path.join(DIR, 'TestReports')
ENGINE_DIR = os.path.join(DIR, 'TestEngines')
CASE_TEMP_DIR = os.path.join(FILE_DIR, 'TempCases')
CONFIG = GetConfig(CONFIG_FILE)

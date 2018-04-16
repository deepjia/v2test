#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import configparser


class GetConfig:
    def __init__(self, file):
        self.config = configparser.ConfigParser()
        self.config.read(file)

    def get(self, section, key):
        return self.config[section][key]


DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if len(sys.argv)==3:
    # for V2Test Management
    TEST_DIR = os.path.join(DIR, 'v2testmgr', 'user', sys.argv[1], sys.argv[2])
    REMOTE_CASE_DIR = CASE_DIR = os.path.join(TEST_DIR, 'RunSuites')
    REMOTE_FILE_DIR = FILE_DIR = os.path.join(TEST_DIR, 'RunFiles')
    REMOTE_REPORT_DIR = REPORT_DIR = os.path.join(TEST_DIR, 'TestReports')
    CONFIG_FILE = os.path.join(TEST_DIR, 'config.ini')
else:
    CASE_DIR = os.path.join(DIR, 'TestSuites')
    FILE_DIR = os.path.join(DIR, 'TestFiles')
    REPORT_DIR = os.path.join(DIR, 'TestReports')
    REMOTE_CASE_DIR = os.path.join(DIR, 'RemoteSuites')
    REMOTE_FILE_DIR = os.path.join(DIR, 'RemoteFiles')
    REMOTE_REPORT_DIR = os.path.join(DIR, 'RemoteReports')
    CONFIG_FILE = os.path.join(DIR, 'config.ini')
ENGINE_DIR = os.path.join(DIR, 'TestEngines')
CASE_TEMP_DIR = os.path.join(FILE_DIR, 'TempSuites')
CONFIG = GetConfig(CONFIG_FILE)
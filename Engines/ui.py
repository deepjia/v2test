#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import platform
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Engines.config import *


platform_os = platform.system()
ext = ('.exe' if platform_os == 'Windows' else '')
OS_TYPE = {'Darwin': 'mac', 'Linux': 'linux', 'Windows': 'win'}[platform_os] + CONFIG.get('UI','BIT')

if CONFIG.get('UI','DRIVER') == 'Safari':
    kw = {}
else:
    DRIVER_FILENAME = {'Firefox': 'geckodriver', 'Chrome': 'chromedriver', 'IE': 'IEDriverServer'}[CONFIG.get('UI','DRIVER')]
    DRIVER_FILE = os.path.join(ENGINE_DIR, OS_TYPE, DRIVER_FILENAME + ext)
    kw = {'executable_path': DRIVER_FILE, 'log_path': os.devnull}


class Test:
    def __init__(self):
        self.driver = getattr(webdriver, CONFIG.get('UI','DRIVER'))(**kw)
        self.driver.implicitly_wait(CONFIG.get('UI','WAIT'))

    # find elements
    def locate(self, locate, locate_value):
        self.last_locate, self.last_locate_value = locate, locate_value
        self.elem = self.driver.find_element(getattr(By, locate.upper()), locate_value)
    # open url
    def open(self, url):
        if url == '':
            url = CONFIG.get('UI','URL')
        return self.driver.get(url)

    def close(self, value):
        self.driver.quit()

    # click element and send text
    def type(self, text):
        self.elem.clear()
        return self.elem.send_keys(text)

    def click(self, value):
        self.elem.click()

    def locate_timeout(self, locate, locate_value, time):
        self.elem = WebDriverWait(self.driver, int(time)).until(
            EC.presence_of_element_located((getattr(By, locate.upper()), locate_value))
        )

    # send keys
    def press(self, key):
        self.elem.clear()
        return self.elem.send_keys(getattr(Keys,key))

    def clean(self):
        self.driver.quit()

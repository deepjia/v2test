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
os_type = {'Darwin': 'mac', 'Linux': 'linux', 'Windows': 'win'}[platform_os] + CONFIG.get('UI', 'BIT')
driver = CONFIG.get('UI', 'DRIVER').title()


def driver_func():
    if driver == 'Safari':
        return webdriver.Safari()
    else:
        driver_file = '.exe' if platform_os == 'Windows' else ''
        driver_file = {'Firefox': 'geckodriver', 'Chrome': 'chromedriver', 'Ie': 'IEDriverServer'}[driver] + driver_file
        driver_file = os.path.join(ENGINE_DIR, os_type, driver_file)
        if driver == 'Ie':
            return webdriver.Ie(driver_file)
        if driver == 'Firefox':
            return webdriver.Firefox(executable_path=driver_file, log_path=None)
        if driver == 'Chrome':
            return webdriver.Chrome(executable_path=driver_file)


class Test:
    def __init__(self):
        pass

    # open url
    def open(self, url):
        self.driver = driver_func()
        self.driver.implicitly_wait(CONFIG.get('UI', 'WAIT'))
        if url == '':
            url = CONFIG.get('UI', 'URL')
        return self.driver.get(url)

    # find elements
    def locate(self, locate, locate_value):
        self.last_locate, self.last_locate_value = locate, locate_value
        self.elem = self.driver.find_element(getattr(By, locate.upper()), locate_value)

    def close(self, value):
        if driver == 'Safari':
            self.driver.quit()
        else:
            self.driver.close()

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
        return self.elem.send_keys(getattr(Keys, key))

    def clean(self):
        if driver != 'Safari':
            try:
                self.driver.close()
            except Exception:
                pass
        try:
            self.driver.quit()
        except Exception:
            pass

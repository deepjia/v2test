#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import platform
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
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
        self.select = self.elem = self.last_locator = self.last_locator_value = self.driver = None

    # find elements
    def locator(self, locator, locator_value, action, action_value):
        # self.last_locator, self.last_locator_value are for action 'save'
        self.last_locator, self.last_locator_value = locator, locator_value
        # waiting is an action which help locating.
        if action == 'waiting':
            if not action_value:
                raise ValueError('This action need a value.')
            self.elem = WebDriverWait(self.driver, int(action_value)).until(
                expected_conditions.presence_of_element_located((getattr(By, locator.upper()), locator_value))
            )
        else:
            self.elem = self.driver.find_element(getattr(By, locator.upper()), locator_value)

    @staticmethod
    def locator_log(locator, locator_value, action, action_value):
        locator_log = locator + (' = ' if locator_value else '') + locator_value
        # waiting is special
        if action == 'waiting':
            return 'Locate ' + locator_log + ' within ' + action_value + 's waiting'
        else:
            return locator_log

    def action(self, action, action_value):
        # Action waiting is processed when locating
        if action == 'open':
            self.driver = driver_func()
            self.driver.implicitly_wait(CONFIG.get('UI', 'WAIT'))
            if not action_value:
                action_value = CONFIG.get('UI', 'URL')
            return self.driver.get(action_value)

        elif action == 'close':
            if driver == 'Safari':
                return self.driver.quit()
            else:
                return self.driver.close()

        elif action == 'type':
            self.elem.clear()
            return self.elem.send_keys(action_value)

        elif action == 'click':
            return self.elem.click()

        elif action == 'press':
            self.elem.clear()
            return self.elem.send_keys(getattr(Keys, action_value))

        elif 'select' in action:
            self.select = Select(self.elem)
            if action_value:
                if action in ('select', 'deselect'):
                    action = action + '_visible_text'
                else:
                    action = action.split('.')[0] + '_by_' + action.split('.')[-1]
                return getattr(self.select, action)(action_value)
            else:
                return getattr(self.select, action + '_all')()

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

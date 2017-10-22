#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import platform
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from TestEngines.config import *


driver = CONFIG.get('UI', 'DRIVER').title()


def driver_func():
    if driver == 'Safari':
        return webdriver.Safari()
    elif driver == 'Remote':
        browser = CONFIG.get('UI', 'REMOTE_BROWSER').upper()
        kwargs = {
            'command_executor': CONFIG.get('UI', 'REMOTE_SERVER'),
            'desired_capabilities': getattr(DesiredCapabilities, browser)
        }
        return webdriver.Remote(**kwargs)
    else:
        # make driver path
        os_name = platform.system()
        driver_dir = {'Darwin': 'mac',
                      'Linux': 'linux',
                      'Windows': 'win'
                      }[os_name] + CONFIG.get('UI', 'BIT')
        driver_file = {'Firefox': 'geckodriver',
                       'Chrome': 'chromedriver',
                       'Ie': 'IEDriverServer'
                       }[driver] + ('.exe' if os_name == 'Windows' else '')
        driver_path = os.path.join(ENGINE_DIR, driver_dir, driver_file)
        # ie, firefox, chrome need more parameters
        if driver == 'Ie':
            return webdriver.Ie(driver_path)
        if driver == 'Firefox':
            return webdriver.Firefox(
                executable_path=driver_path, log_path=None)
        if driver == 'Chrome':
            return webdriver.Chrome(executable_path=driver_path)


class Test:
    def __init__(self):
        self.driver = None
        self.select = None
        self.elem = None
        self.last_locator = None
        self.last_locator_value = None

    # find elements
    def locator(self, locator, locator_value, action, action_value):
        # saved for action 'save'
        self.last_locator, self.last_locator_value = locator, locator_value
        # waiting is an action which acts when locating.
        if action == 'waiting':
            if not action_value:
                raise ValueError('This action need a value.')
            self.elem = WebDriverWait(self.driver, int(action_value)).until(
                expected_conditions.presence_of_element_located(
                    (getattr(By, locator.upper()), locator_value)
                )
            )
        else:
            self.elem = self.driver.find_element(
                getattr(By, locator.upper()), locator_value)

    @staticmethod
    def locator_log(locator, locator_value, action, action_value):
        log = locator + (' = ' if locator_value else '') + locator_value
        # waiting acts when locating.
        if action == 'waiting':
            return 'Locate ' + log + ' within ' + action_value + 's waiting'
        else:
            return log

    def action(self, action_value, action, *action_sub):
        # action waiting is processed when locating
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

        elif action in ('select', 'deselect'):
            self.select = Select(self.elem)
            # (de)select all
            if not action_value:
                return getattr(self.select, action + '_all')()
            # select by action_sub
            if action_sub:
                action = action + '_by_' + action_sub[0]
            # select by visible_text by default
            else:
                action = action + '_visible_text'
            return getattr(self.select, action)(action_value)

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

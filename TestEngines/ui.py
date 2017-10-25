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
        self.last_location = None

    # find elements
    def locator(self, locator, location, action, value):
        # saved for action 'save'
        self.last_locator, self.last_location = locator, location
        # waiting is an action which acts when locating.
        if action == 'waiting':
            if not value:
                raise ValueError('This action need a value.')
            self.elem = WebDriverWait(self.driver, int(value)).until(
                expected_conditions.presence_of_element_located(
                    (getattr(By, locator.upper()), location)
                )
            )
        else:
            self.elem = self.driver.find_element(
                getattr(By, locator.upper()), location)

    @staticmethod
    def locator_log(locator, location, action, value):
        log = locator + (' = ' if location else '') + location
        # waiting acts when locating.
        if action == 'waiting':
            return 'Locate ' + log + ' within ' + value + 's waiting'
        else:
            return log

    def action(self, value, action, *action_sub):
        # action waiting is processed when locating
        if action == 'open':
            self.driver = driver_func()
            self.driver.implicitly_wait(CONFIG.get('UI', 'WAIT'))
            if not value:
                value = CONFIG.get('UI', 'URL')
            return self.driver.get(value)

        elif action == 'close':
            if driver == 'Safari':
                return self.driver.quit()
            else:
                return self.driver.close()

        elif action == 'type':
            self.elem.clear()
            return self.elem.send_keys(value)

        elif action in ('click', 'is_selected', 'is_displayed', 'is_enabled'):
            return getattr(self.elem, action)()

        elif action == 'press':
            self.elem.clear()
            return self.elem.send_keys(getattr(Keys, value))

        elif action in ('text', 'tag_name'):
            return getattr(self.elem, action)

        elif action == 'get_attribute':
            if not action_sub:
                raise ValueError('Action get_attribute need a sub-action.')
            return self.elem.get_attribute(action_sub[0])

        elif action == 'get_property':
            if not action_sub:
                raise ValueError('Action get_property need a sub-action.')
            return self.elem.get_property(action_sub[0])

        elif action in ('select', 'deselect'):
            self.select = Select(self.elem)
            # (de)select all
            if not value:
                return getattr(self.select, action + '_all')()
            # select by action_sub
            if action_sub:
                action = action + '_by_' + action_sub[0]
            # select by visible_text by default
            else:
                action = action + '_visible_text'
            return getattr(self.select, action)(value)

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

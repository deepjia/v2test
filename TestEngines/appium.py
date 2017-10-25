from appium import webdriver
from ast import literal_eval
from appium.webdriver.common.touch_action import TouchAction
# from appium.webdriver.common.multi_action import MultiAction
from TestEngines.config import *


desired_caps = {
    'platformName': CONFIG.get('APPIUM', 'PLATFORM_NAME'),
    'platformVersion': CONFIG.get('APPIUM', 'PLATFORM_VERSION'),
    'deviceName': CONFIG.get('APPIUM', 'DEVICE_Name'),
    'app': os.path.join(FILE_DIR, CONFIG.get('APPIUM', 'APP')),
    'automationName': CONFIG.get('APPIUM', 'automationName'),
}


class Test:
    def __init__(self):
        self.select = None
        self.elem = None
        self.last_locator = None
        self.last_location = None
        self.driver = webdriver.Remote(
            CONFIG.get('APPIUM', 'REMOTE_SERVER'), desired_caps)
        self.x = self.y = None
        self.touch_action = None

    # find elements
    def locator(self, locator, location, action, value):
        # saved for action 'save'
        self.last_locator, self.last_location = locator, location
        # waiting is an action which acts when locating.
        if action == 'waiting':
            if not value:
                raise ValueError('This action need a value.')
            self.driver.wait_activity()
        if locator in ('x', 'y'):
            setattr(self, locator, int(value))
        elif locator in ('ios_uiautomation',
                         'android_uiautomator',
                         'ios_predicate',
                         'accessibility_id',
                         'class_name',
                         'xpath'):
            self.elem = getattr(
                self.driver, 'find_element_by_' + locator)(value)

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
        if action == 'switch_to':
            if not value:
                value = None
            return self.driver.switch_to.context(value)

        elif action in ('lock',
                        'background_app',
                        'keyevent'):
            return getattr(self.driver, action)(int(value))

        elif action in ('is_app_installed',
                        'install_app',
                        'remove_app',
                        'pull_file',):
            return getattr(self.driver, action)(value)

        elif action in ('hide_keyboard',
                        'open_notifications',
                        'shake', 'close_app',
                        'launch_app',
                        'reset'):
            return getattr(self.driver, action)()

        elif action in ('current_context',
                        'contexts',
                        'app_strings',
                        'current_activity'):
            return getattr(self.driver, action)

        elif action in ('start_activity', 'swipe'):
            args = literal_eval(value)
            self.driver.start_activity(*args)

        # TouchAction
        elif action == 'touch_action{':
            self.touch_action = TouchAction(self.driver)

        elif action == '}':
            self.touch_action.perform()
            self.touch_action = None

        elif action in ('tap', 'press',  'long_press', 'release', 'move_to'):
            kwargs = {}
            if action == 'tap':
                kwargs['element'] = self.elem
                kwargs['x'] = self.x
                kwargs['y'] = self.y
                kwargs['count'] = int(value) if value else 1
            elif action == 'press' or action == 'move_to':
                kwargs['element'] = self.elem
                kwargs['x'] = self.x
                kwargs['y'] = self.y
            elif action == 'long_press':
                kwargs['element'] = self.elem
                kwargs['x'] = self.x
                kwargs['y'] = self.y
                kwargs['duration'] = int(value) if value else 1000
            if self.touch_action:
                self.touch_action = getattr(self.touch_action, action)(**kwargs)
            else:
                getattr(TouchAction(self.driver), action)(**kwargs).perform()
                self.x = self.y = None

        # other actions
        elif action in ('zoom', 'pinch'):
            getattr(self.driver, action)(self.elem)

        elif action == 'scroll':
            self.driver.scroll(None, self.elem)

        elif action == 'open':
            self.driver.implicitly_wait(CONFIG.get('UI', 'WAIT'))
            if not value:
                value = CONFIG.get('UI', 'URL')
            return self.driver.get(value)

        elif action == 'close':
                return self.driver.close()

        elif action == 'type':
            self.elem.clear()
            return self.elem.send_keys(value)

        elif action in ('click', 'is_selected', 'is_displayed', 'is_enabled'):
            return getattr(self.elem, action)()

        elif action in ('text', 'tag_name'):
            return getattr(self.elem, action)

        elif action in ('get_attribute', 'get_property'):
            if not action_sub:
                raise ValueError('Action need a sub-action.')
            return getattr(self.elem, action)(action_sub[0])

    def clean(self):
        try:
            self.driver.quit()
        except Exception:
            pass

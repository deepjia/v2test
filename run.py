#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import unittest
import logging
import HtmlTestRunner
import Engines.ui
import Engines.http
import Engines.shell
import Engines.mysql
from datetime import datetime
from Engines.config import *
from Engines.excel import *
from Engines.ddt import *


COL_RUN_RESULT = 10
COL_RUN_TIME = 11
COL_RUN_ERROR = 12
LEN_MSG = int(CONFIG.get('MAIN', 'LEN_MSG'))

saved_elements = {}
check = {'equal': 'assertEqual', 'in': 'assertIn', '!equal': 'assertNotEqual', '!in': 'assertNotIn'}
logging.basicConfig(level=getattr(logging, CONFIG.get('MAIN', 'LOG_LEVEL')),
                    format='%(asctime)s - %(levelname)s: %(message)s')
print('Loading cases...\n' + '-' * 70)
print('\n'.join(CASE_FILES))
cases_all = [case for file in CASE_FILES for case in ReadAndFormatExcel(file).cases]


@ddt
class RunTest(unittest.TestCase):
    def setUp(self):
        """Init Case"""

    @idata(cases_all)
    def test_Case(self, case):
        """[ {0[0][10]} | {0[0][11]} ] {0[0][1]}: {0[0][2]}"""
        logging.info("")
        file, file_name, sheet_name, case_row, case_id, case_name, engine = [case[0][column] for column in
                                                                             (9, 10, 11, 12, 1, 2, 4)]
        result = [(sheet_name, case_row, COL_RUN_TIME, str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))]
        i = None
        try:
            # one case: case[line][column]
            self.run = getattr(Engines, engine.lower()).Test()
            logging.info('[Sheet] ' + file_name + ' | ' + sheet_name)
            logging.info('[Case] ' + case_id + ': ' + case_name)
            # read lines from case
            for i in range(0, len(case)):
                locator, locator_value, action, action_value = [str(case[i][column])
                                                                if case[i][column] else '' for column in (5, 6, 7, 8)]
                locator, action = locator.lower(), action.lower()
                # locate elements or encapsulate params
                if locator:
                    if locator == 'saved':
                        logging.info('[Step] {Element} Saved = ' + locator_value)
                        locator, locator_value = saved_elements[locator_value]
                    logging.info('[Step] {Element} ' +
                                 self.run.locator_log(locator, locator_value, action, action_value))
                    self.run.locator(locator, locator_value, action, action_value)

                if action:
                    action_list = action.split('.')

                    # actions by framework
                    if action_list[0] == 'log':
                        message = response if action == 'log' else getattr(response, action_list[-1])
                        logging.info('[Step] Response ' + ' = ' + str(message))

                    elif action == 'save':
                        if not action_value:
                            self.fail('This action need a value')
                        logging.info('[Step] Element ' + 'saved to ' + action_value)
                        saved_elements[action_value] = (self.run.last_locator, self.run.last_locator_value)

                    elif action == 'wait':
                        if not action_value:
                            self.fail('This action need a value')
                        logging.info('[Step] ' + action.title() + ' = ' + action_value)
                        time.sleep(int(action_value))

                    elif action_list[0] in check:
                        if not action_value:
                            self.fail('This action need a value')
                        message = str(response if len(action_list) == 1 else getattr(response, action_list[-1]))
                        logging.info('[Step] Check ' + action_value + ' ' + action + ' ' +
                                     message.replace('\n', '')[0:LEN_MSG] + ' /* Use log action to show more */')
                        getattr(self, check[action_list[0]])(action_value, message)

                    # actions by engine
                    else:
                        logging.info('[Step] ' + action.title() + ' | ' + action_value)
                        response = self.run.action(action_value, *action_list)

        except Exception as e:
            i = str(i + 1 if i else i)
            self.e = '[Line ' + i + '] ' + str(e)
            result.append((sheet_name, case_row, COL_RUN_RESULT, 'fail'))
            # raise
        else:
            self.e = ''
            result.append((sheet_name, case_row, COL_RUN_RESULT, 'pass'))
        finally:
            result.append((sheet_name, case_row, COL_RUN_ERROR, self.e))
            write_excel(file, result)

    def tearDown(self):
        """Do some cleaning"""
        self.run.clean()
        if self.e:
            self.fail(self.e)
        logging.info('[Case] End.')


if __name__ == '__main__':
    unittest.main(testRunner=HtmlTestRunner.HTMLTestRunner(output=REPORT_DIR, report_title='V2Test Report'))

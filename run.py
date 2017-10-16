#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import unittest
import logging
import HtmlTestRunner
import TestEngines.ui
import TestEngines.http
import TestEngines.shell
import TestEngines.mysql
import TestEngines.locust
from datetime import datetime
from TestEngines.config import *
from TestEngines.excel import *
from TestEngines.ddt import *


COL_RUN_RESULT = 10
COL_RUN_TIME = 11
COL_RUN_ERROR = 12
LEN_MSG = int(CONFIG.get('MAIN', 'LEN_MSG'))

saved_elements = {}
check = {'equal': 'assertEqual',
         '!equal': 'assertNotEqual',
         'in': 'assertIn',
         '!in': 'assertNotIn',
         'log':''}
logging.basicConfig(level=getattr(logging, CONFIG.get('MAIN', 'LOG_LEVEL')),
                    format='%(asctime)s - %(levelname)s: %(message)s')
case_files = [x.path for x in os.scandir(CASE_DIR) if
              x.is_file() and x.name.endswith(".xlsx") and '~$' not in x.name]
cases_all = (case for file in case_files for case in ReadAndFormatExcel(file).cases)


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
            self.run = getattr(TestEngines, engine.lower()).Test()
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
                    action_name, *action_args = action.split('.')

                    # actions by framework
                    if action_name == 'save':
                        if not action_value:
                            self.fail('This action need a value')
                        logging.info('[Step] Element ' + 'saved to ' + action_value)
                        saved_elements[action_value] = (self.run.last_locator, self.run.last_locator_value)

                    elif action_name == 'wait':
                        if not action_value:
                            self.fail('This action need a value')
                        logging.info('[Step] ' + action.title() + ' = ' + action_value)
                        time.sleep(int(action_value))

                    elif action_name in check:
                        message = str(self.run.check(response, *action_args) if action_args else response)
                        if action_name == 'log':
                            logging.info('[Step] Response ' + ' = ' + str(message))
                        else:
                            logging.info('[Step] Check ' + action_value + ' ' + action + ' ' +
                                     message.replace('\n', '')[0:LEN_MSG] + ' /* Use log action to show more */')
                            getattr(self, check[action_name])(action_value, message)

                    # actions by engine
                    else:
                        logging.info('[Step] ' + action.title() + ' | ' + action_value)
                        response = self.run.action(action_value, action_name, *action_args)

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
    print('Loading cases...\n' + '-' * 70)
    print('\n'.join(case_files))
    unittest.main(testRunner=HtmlTestRunner.HTMLTestRunner(output=REPORT_DIR, report_title='V2Test Report'))

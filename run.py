#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import unittest
import ddt
import logging
import HtmlTestRunner
import Engines.ui
import Engines.http
import Engines.shell
from datetime import datetime
from Engines.config import *
from Engines.excel import *


COL_RUN_RESULT = 10
COL_RUN_TIME = 11
COL_RUN_ERROR = 12
LEN_MSG = 500

cases_all = []
saved_elements = {}
check = {'equal': 'assertEqual', 'in': 'assertIn', '!equal': 'assertNotEqual', '!in': 'assertNotIn'}
logging.basicConfig(level=getattr(logging, CONFIG.get('MAIN', 'LOG_LEVEL')),
                    format='%(asctime)s - %(levelname)s: %(message)s')
print('Loading cases...\n' + '-' * 70)
for x in CASE_FILES:
    logging.info(x)
    cases_all += load_cases(x)


def write_results(file, results):
    file_type = check_excel_version(file)
    excel = eval(file_type)(file)
    excel.write_cells(results)


@ddt.ddt
class RunTest(unittest.TestCase):
    def setUp(self):
        """Init Case"""
        logging.info('')

    @ddt.data(*cases_all)
    def test_Case(self, data):
        """[ {0[0][10]} | {0[0][11]} ] {0[0][1]}: {0[0][2]}"""
        file, file_name, sheet_name, case_row, case_id, case_name, engine = [data[0][column] for column in
                                                                             (9, 10, 11, 12, 1, 2, 4)]
        result = [(sheet_name, case_row, COL_RUN_TIME, str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))]
        i = None
        try:
            # one data one case: data[line][column]
            self.run = getattr(Engines, engine.lower()).Test()
            logging.info('[Sheet] ' + file_name + ' | ' + sheet_name)
            logging.info('[Case] ' + case_id + ': ' + case_name)
            # read lines from data
            for i in range(0, len(data)):
                locator, locator_value, action, action_value = [str(data[i][column])
                                                                if data[i][column] else '' for column in (5, 6, 7, 8)]
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
                    # actions by engine
                    if action_list[0] in ('click', 'close', 'open', 'type', 'press', 'select', 'deselect',
                                          'get', 'post', 'head', 'put', 'delete', 'options', 'cmd', 'file'):
                        logging.info('[Step] ' + action.title() + ' | ' + action_value)
                        response = self.run.action(action, action_value)

                    # actions by framework
                    elif action_list[0] == 'log':
                        message = response if action == 'log' else getattr(response, action_list[-1])
                        logging.info('[Step] Response ' + ' = ' + str(message))

                    elif not action_value:
                        self.fail('This action need a value')

                    elif action == 'save':
                        logging.info('[Step] Element ' + 'saved to ' + action_value)
                        saved_elements[action_value] = (self.run.last_locator, self.run.last_locator_value)

                    elif action == 'wait':
                        logging.info('[Step] ' + action.title() + ' = ' + action_value)
                        time.sleep(int(action_value))

                    # action check
                    elif action_list[0] in check:
                        message = str(response if len(action_list) == 1 else getattr(response, action_list[-1]))
                        logging.info('[Step] Check ' + action_value + ' ' + action + ' ' +
                                     message.replace('\n', '')[0:LEN_MSG] + ' (Use log action to show more)')
                        getattr(self, check[action_list[0]])(action_value, message)

        except Exception as e:
            i = str(i + 1 if i else i)
            self.e = '[Line ' + i + '] ' + str(e)
            result.append((sheet_name, case_row, COL_RUN_RESULT, 'fail'))
            raise
        else:
            self.e = ''
            result.append((sheet_name, case_row, COL_RUN_RESULT, 'pass'))
        finally:
            result.append((sheet_name, case_row, COL_RUN_ERROR, self.e))
            write_results(file, result)

    def tearDown(self):
        """Do some cleaning"""
        self.run.clean()
        if self.e:
            self.fail(self.e)
        logging.info('[Case] End.')


if __name__ == '__main__':
    unittest.main(testRunner=HtmlTestRunner.HTMLTestRunner(output=REPORT_DIR, report_title='V2Test Report'))

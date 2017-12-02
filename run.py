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

logging.basicConfig(
    level=getattr(logging, CONFIG.get('MAIN', 'LOG_LEVEL')),
    format='%(asctime)s - %(levelname)s: %(message)s')

case_files = [x.path for x in os.scandir(CASE_DIR) if x.is_file()
              and x.name.endswith(".xlsx") and '~$' not in x.name]

cases_all = (case for file in case_files
             for case in ReadAndFormatExcel(file).cases)


@ddt
class RunTest(unittest.TestCase):
    def setUp(self):
        """Init Case"""

    @idata(cases_all)
    def test_Case(self, case):
        """[ {0[0][10]} | {0[0][11]} ] {0[0][1]}: {0[0][2]}"""
        logging.info("")

        file, file_name, sheet_name, case_row, case_id, case_name, engine = [
            case[0][column] for column in (9, 10, 11, 12, 1, 2, 4)]

        result = [(sheet_name, case_row, COL_RUN_TIME,
                   str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))]
        i = None
        try:
            # one case: case[line][column]
            self.run = getattr(TestEngines, engine.lower()).Test()
            logging.info('[Sheet] ' + file_name + ' | ' + sheet_name)
            logging.info('[Case] ' + case_id + ': ' + case_name)
            # read lines from case
            for i in range(0, len(case)):
                locator, location, action, value = [
                    str(case[i][column] or '') for column in (5, 6, 7, 8)]
                locator, action = locator.lower(), action.lower()

                # locate elements or encapsulate params
                if locator:
                    # saved is a locator powered by framework
                    if locator == 'saved':
                        logging.info('[Step] {Element} Saved = ' + location)
                        locator, location = saved_elements[location]
                    # other locator powered by engines
                    logging.info('[Step] {Element} ' + self.run.locator_log(
                        locator, location, action, value))
                    self.run.locator(locator, location, action, value)

                if action:
                    action_name, *action_args = action.split('.')
                    # actions by framework
                    if action_name == 'save':
                        if not value:
                            self.fail('This action need a value')
                        logging.info('[Step] Element ' + 'saved to ' + value)
                        saved_elements[value] = (
                            self.run.last_locator, self.run.last_location)

                    elif action_name == 'wait':
                        if not value:
                            self.fail('This action need a value')
                        logging.info('[Step] ' + action.title() + ' = ' + value)
                        time.sleep(int(value))

                    elif action_name in check:
                        message = str(
                            self.run.check(response, *action_args) if action_args
                            else response)
                        if action_name == 'log':
                            logging.info('[Step] Response ' + ' = ' + message)
                        else:
                            logging.info(
                                '[Step] Check ' + value + ' ' + action + ' '
                                + message.replace('\n', '')[0:LEN_MSG]
                                + ' /* Use log action to show more */')
                            getattr(self, check[action_name])(value, message)

                    # actions by engine
                    else:
                        logging.info('[Step] ' + action.title() + ' | ' + value)
                        response = self.run.action(
                            value, action_name, *action_args)

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
    unittest.main(testRunner=HtmlTestRunner.HTMLTestRunner(
        output=REPORT_DIR, report_title='V2Test Report'))

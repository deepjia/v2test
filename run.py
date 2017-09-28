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


cases_all = []
saved_elements={}
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
        file, file_name, sheet_name, case_row, case_id, case_name, engine = [data[0][x] for x in (9,10,11,12,1,2,4)]
        result = [(sheet_name, case_row, 11, str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))]
        i = None
        try:
            # one data one case: data[line][column]
            self.run = getattr(Engines, engine.lower()).Test()
            logging.info('[Sheet] ' + file_name + ' | ' + sheet_name)
            logging.info('[Case] ' + data[0][1] + ': ' + data[0][2])
            # read lines from data
            for i in range(0, len(data)):
                locator, locator_value, action, action_value = \
                    data[i][5], str(data[i][6]) if data[i][6] else '', \
                    data[i][7], str(data[i][8]) if data[i][8] else ''

                # locate elements or encapsulate params
                if locator:
                    if locator == 'saved':
                        logging.info('[Step] {Element.saved} ' + locator_value)
                        locator, locator_value = saved_elements[locator_value]
                    if action == 'wait.element':
                        if not action_value:
                            self.fail('This action need a value.')
                            # raise ValueError('Need a value')
                        logging.info('[Step] {Element} ' + locator + ' = ' + locator_value +
                                     ' wait.element for | ' + action_value + ' s')

                        self.run.locator_timeout(locator, locator_value, action_value)
                    else:
                        logging.info('[Step] {Element/Parameter} ' + locator + (' = ' if locator_value else '') + locator_value)
                        self.run.locator(locator, locator_value)

                if action:
                    # actions by engine
                    if action in ('click', 'close', 'open', 'type', 'press', 'get', 'post', 'cmd', 'file'):
                        logging.info('[Step] ' + action.title() + ' | ' + action_value)
                        response = getattr(self.run, action)(action_value)

                    # actions by framework
                    elif not action_value:
                        self.fail('This action need a value')

                    elif action == 'save':
                        logging.info('[Step] Element ' + action.lower() + 'd to ' + action_value)
                        saved_elements[action_value] = (self.run.last_locator, self.run.last_locator_value)

                    elif action == 'wait':
                        logging.info('[Step] ' + action.title() + ' = ' + action_value)
                        time.sleep(int(action_value))

                    elif action == 'log':
                        logging.info('[Step] Response ' + ' = ' + str(response))

                    elif action.lower().split('.')[0] == 'log':
                        message = getattr(response, action.lower().split('.')[-1])
                        logging.info('[Step] Response ' + ' = ' + str(message))

                    # action check (response)
                    elif action.lower() in check:
                        logging.info('[Step] Check ' + action_value + ' ' + action.lower() + ' ' +
                                     str(response).replace('\n', '')[0:500] + ' (Use log action to show more)')
                        getattr(self, check[action.lower()])(action_value, response)

                    # action check (response.attribute)
                    elif action.lower().split('.')[0] in check:
                        message = getattr(response, action.lower().split('.')[-1])
                        message = str(message)
                        logging.info('[Step] Check ' + action_value + ' ' + action.lower() + ' ' +
                                     message.replace('\n', '')[0:500] + ' (Use log action to show more)')
                        getattr(self, check[action.lower().split('.')[0]])(action_value, message)

        except Exception as e:
            # File, sheet, row, column, value
            i = str(i + 1 if i else i)
            self.e = '[Line ' + i + '] ' + str(e)
            result.append((sheet_name, case_row, 10, 'fail'))
            raise
        else:
            self.e = ''
            result.append((sheet_name, case_row, 10, 'pass'))
        finally:
            result.append((sheet_name, case_row, 12, self.e))
            write_results(file, result)

    def tearDown(self):
        """Do some cleaning"""
        self.run.clean()
        if self.e:
            self.fail(self.e)
        logging.info('[Case] End.')


if __name__ == '__main__':
    unittest.main(testRunner=HtmlTestRunner.HTMLTestRunner(output=REPORT_DIR, report_title='V2Test Report'))

import unittest
import sqlite3
from .test_pomodorro import TestPomodorro
from .test_task import TestTask
from .test_pomodorro_log import TestPomodorroLog
from .test_task_log import TestTaskLog
from .test_settings import TestSettings
from .test_model import TestModel
from ..app.model import Model
import sys
import os
import time

def get_tests_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

def suite():
    suite = unittest.TestSuite()

    # Constructors Test
    suite.addTest(TestTask('test_constructor'))
    suite.addTest(TestPomodorro('test_constructor'))
    suite.addTest(TestTaskLog('test_constructor'))
    suite.addTest(TestPomodorroLog('test_constructor'))

    # Model tests
    suite.addTest(TestModel('test_get_settings'))
    suite.addTest(TestModel('test_get_task_log'))
    suite.addTest(TestModel('test_get_pomodorro_log'))
    suite.addTest(TestModel('test_settings_set'))
    suite.addTest(TestModel('test_add_task'))
    suite.addTest(TestModel('test_delete_task'))
    suite.addTest(TestModel('test_edit_task'))
    suite.addTest(TestModel('test_add_pomodorro'))
    suite.addTest(TestModel('test_delete_pomodorro'))
    suite.addTest(TestModel('test_change_tag'))
    suite.addTest(TestModel('test_change_goal'))
    suite.addTest(TestModel('test_edit_pomodorro'))
    suite.addTest(TestModel('test_get_active_pomodorro'))
    suite.addTest(TestModel('test_is_complete'))
    suite.addTest(TestModel('test_set_active_pomodorro'))
    suite.addTest(TestModel('test_begin_pomodorro'))
    suite.addTest(TestModel('test_reset_pomodorro'))
    suite.addTest(TestModel('test_complete_pomodorro'))
    suite.addTest(TestModel('test_complete_task'))
    suite.addTest(TestModel('test_expire_pomodorro'))
    suite.addTest(TestModel('test_edit_pomodorro_due'))
    suite.addTest(TestModel('test_epoch_to_local'))

    # Pomodorro tests
    suite.addTest(TestPomodorro('test_repr'))

    # PomodorroLog tests
    suite.addTest(TestPomodorroLog('test_get_pomodorro'))
    suite.addTest(TestPomodorroLog('test_add'))
    suite.addTest(TestPomodorroLog('test_delete'))


    return suite

if __name__ == '__main__':

    test_db_path = get_tests_path() + '/test.db'
    conn = sqlite3.connect(test_db_path)
    model = Model(conn)
    try:
        model.initialize_tables()
    except sqlite3.OperationalError:
        # tables already exist.
        print('Removing old instance of test database...')
        os.remove(test_db_path)
        time.sleep(0.001)
        model.initialize_tables()
    print("Initialized new test database...")
    
    print('Running tests...')
    runner = unittest.TextTestRunner()
    runner.run(suite())

    print('Removing test database...')
    os.remove(test_db_path)
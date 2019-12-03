import unittest
from test_pomodorro import TestPomodorro
from test_task import TestTask
from test_pomodorro_log import TestPomodorroLog
from test_task_log import TestTaskLog
from test_settings import TestSettings

def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestTask('test_constructor'))
    suite.addTest(TestPomodorro('test_constructor'))
    suite.addTest(TestTaskLog('test_constructor'))
    suite.addTest(TestPomodorroLog('test_constructor'))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
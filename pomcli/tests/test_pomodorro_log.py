import unittest
from pomcli.app.pomodorro_log import PomodorroLog
from pomcli.app.task_log import TaskLog
from datetime import datetime

class TestPomodorroLog(unittest.TestCase):

    def setUp(self):
        
        self.tasks = [
            [1, "Task 1", "daily", datetime.now(), datetime.now(), False, False],
            [2, "Task 2", "daily", datetime.now(), datetime.now(), False, True],
            [3, "Task 3", "daily", datetime.now(), datetime.now(), True, False],
            [4, "Task 4", "daily", datetime.now(), datetime.now(), True, True],
            [5, "Task 5", "daily", datetime.now(), datetime.now(), False, True],
        ]

        self.pomodorros = [
            [1, "Pom 1", 1, 25, 5, "goal 1", False, False, datetime.now(), datetime.now(), 10, None],
            [2, "Pom 2", 1, 25, 5, "goal 2", False, False, datetime.now(), datetime.now(), 10, None],
            [3, "Pom 3", 2, 25, 5, "goal 3", False, False, datetime.now(), datetime.now(), 10, None],
            [4, "Pom 4", 2, 25, 5, "goal 4", False, False, datetime.now(), datetime.now(), 10, None],
            [5, "Pom 5", 2, 25, 5, "goal 5", False, False, datetime.now(), datetime.now(), 10, None],
        ]
        
        self.model = None
        self.settings = None
        self.tl = TaskLog(self.tasks, self.model, self.settings)
        self.pl = PomodorroLog(self.pomodorros, self.model, self.settings, self.tl)

    def test_constructor(self):
        self.assertEqual(self.pl[1].tag, "Pom 1")
        self.assertEqual(self.pl["Pom 1"].pom_id, 1)
        self.assertEqual(len(self.pl), len(self.pomodorros)*2) # cached under id and name
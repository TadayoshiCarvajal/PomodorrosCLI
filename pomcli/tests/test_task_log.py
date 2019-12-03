import unittest
from pomcli.app.task_log import TaskLog

class TestTaskLog(unittest.TestCase):

    def setUp(self):
        """ Task variables:
        self.task_id = task_id
        self.name = name
        self.repeats = repeats
        self.last_refresh = last_refresh
        self.next_refresh = next_refresh
        self.deleted = deleted
        self.completed = completed
        """
        from datetime import datetime

        self.tasks = [
            [1, "Task 1", "daily", datetime.now(), datetime.now(), False, False],
            [2, "Task 2", "daily", datetime.now(), datetime.now(), False, True],
            [3, "Task 3", "daily", datetime.now(), datetime.now(), True, False],
            [4, "Task 4", "daily", datetime.now(), datetime.now(), True, True],
            [5, "Task 5", "daily", datetime.now(), datetime.now(), False, True],
        ]

        self.model = None
        self.settings = None

        self.tl = TaskLog(self.tasks, self.model, self.settings)

    def test_constructor(self):
        i = 1
        for task in self.tasks:
            self.assertEqual(self.tl[i].task_id, task[0])
            self.assertEqual(self.tl[i].name, task[1])
            self.assertEqual(self.tl[i].repeats, task[2])
            self.assertEqual(self.tl[i].last_refresh, task[3])
            self.assertEqual(self.tl[i].next_refresh, task[4])
            self.assertEqual(self.tl[i].deleted, task[5])
            self.assertEqual(self.tl[i].completed, task[6])
            i += 1
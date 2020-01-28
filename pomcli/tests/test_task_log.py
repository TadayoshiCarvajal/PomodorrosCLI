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
            [1, "Task 1", "daily", 5, 25, 5, "", False, False],
            [2, "Task 2", "daily", 5, 25, 5, "", False, False],
            [3, "Task 3", "daily", 5, 25, 5, "", False, False],
            [4, "Task 4", "daily", 5, 25, 5, "", False, False],
            [5, "Task 5", "daily", 5, 25, 5, "", False, False],
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
            self.assertEqual(self.tl[i].priority, task[3])
            self.assertEqual(self.tl[i].pomodorro_length, task[4])
            self.assertEqual(self.tl[i].rest_length, task[5])
            self.assertEqual(self.tl[i].refresh_frequency, task[6])
            self.assertEqual(self.tl[i].completed, task[7])
            self.assertEqual(self.tl[i].pomodorro_complete, task[8])
            i += 1
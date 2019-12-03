import unittest
import sys
from pomcli.app.task import Task

class TestTask(unittest.TestCase):

    def setUp(self):
        from datetime import datetime
        self.task_id = 123
        self.name = "Laundry"
        self.repeats = "daily"
        self.last_refresh = datetime(2019, 8, 16)
        self.next_refresh = datetime(2019, 12, 1)
        self.deleted = False
        self.completed = False

        self.t = Task(self.task_id, self.name, self.repeats, self.last_refresh,
                    self.next_refresh, self.deleted, self.completed)

    def test_constructor(self):
        self.assertEqual(self.t.task_id, self.task_id)
        self.assertEqual(self.t.name, self.name)
        self.assertEqual(self.t.repeats, self.repeats)
        self.assertEqual(self.t.last_refresh, self.last_refresh)
        self.assertEqual(self.t.next_refresh, self.next_refresh)
        self.assertFalse(self.deleted)
        self.assertFalse(self.completed)
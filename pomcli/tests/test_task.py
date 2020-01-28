import unittest
import sys
from pomcli.app.task import Task

class TestTask(unittest.TestCase):

    def setUp(self):
        self.task_id = 123
        self.name = "Laundry"
        self.repeats = "daily"
        self.priority = 5
        self.pomodorro_length = 25
        self.rest_length = 25
        self.refresh_frequency = ""
        self.completed = False
        self.pomodorro_complete = False

        self.t = Task(self.task_id, self.name, self.repeats, self.priority, 
                    self.pomodorro_length, self.rest_length, self.refresh_frequency, 
                    self.completed, self.pomodorro_complete)

    def test_constructor(self):
        self.assertEqual(self.t.task_id, self.task_id)
        self.assertEqual(self.t.name, self.name)
        self.assertEqual(self.t.repeats, self.repeats)
        self.assertEqual(self.t.priority, self.priority)
        self.assertEqual(self.t.pomodorro_length, self.pomodorro_length)
        self.assertEqual(self.t.rest_length, self.rest_length)
        self.assertEqual(self.t.refresh_frequency, self.refresh_frequency)
        self.assertFalse(self.t.completed)
        self.assertFalse(self.t.pomodorro_complete)
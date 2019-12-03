import unittest
import sys
from pomcli.app.pomodorro import Pomodorro
#print(sys.path)
class TestPomodorro(unittest.TestCase):

    def setUp(self):
        from datetime import datetime
        self.pom_id = 1
        self.tag = "do laundry"
        self.task = "Laundry"
        self.length = 25
        self.rest = 5
        self.goal = "separate darks, whites, and colors. Put first load in."
        self.active = False
        self.completed = True
        self.start_time = datetime.now()
        self.end_time = datetime.now()
        self.time_spent = 1000
        self.historic_tag = None
        
        self.p = Pomodorro(self.pom_id, self.tag, self.task, self.length, self.rest, 
                            self.goal, self.active, self.completed, self.start_time, self.end_time,
                            self.time_spent, self.historic_tag)

    def test_constructor(self):
        self.assertEqual(self.p.pom_id, self.pom_id)
        self.assertEqual(self.p.tag, self.tag)
        self.assertEqual(self.p.task, self.task)
        self.assertEqual(self.p.length, self.length)
        self.assertEqual(self.p.rest, self.rest)
        self.assertEqual(self.p.goal, self.goal)
        self.assertFalse(self.p.active)
        self.assertTrue(self.p.completed)
        self.assertEqual(self.p.start_time, self.start_time)
        self.assertEqual(self.p.end_time, self.end_time)
        self.assertEqual(self.p.time_spent, self.time_spent)
        self.assertEqual(self.p.historic_tag, self.historic_tag)
import unittest
import sys
from ..app.pomodorro import Pomodorro

class TestPomodorro(unittest.TestCase):

    def setUp(self):
        from datetime import datetime
        self.pom_id = 1
        self.tag = "do laundry"
        self.priority = 5
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
        self.expired = False
        self.due = datetime.now()
        
        self.p = Pomodorro(self.pom_id, self.tag, self.task, self.priority, 
                            self.length, self.rest, self.goal, self.active, 
                            self.completed, self.start_time, self.end_time,
                            self.time_spent, self.historic_tag, self.expired,
                            self.due)

    def test_constructor(self):
        self.assertEqual(self.p.pom_id, self.pom_id)
        self.assertEqual(self.p.tag, self.tag)
        self.assertEqual(self.p.task, self.task)
        self.assertEqual(self.p.priority, self.priority)
        self.assertEqual(self.p.length, self.length)
        self.assertEqual(self.p.rest, self.rest)
        self.assertEqual(self.p.goal, self.goal)
        self.assertFalse(self.p.active)
        self.assertTrue(self.p.completed)
        self.assertEqual(self.p.start_time, self.start_time)
        self.assertEqual(self.p.end_time, self.end_time)
        self.assertEqual(self.p.time_spent, self.time_spent)
        self.assertEqual(self.p.historic_tag, self.historic_tag)
        self.assertEqual(self.p.expired, self.expired)
        self.assertEqual(self.p.due, self.due)

    def test_repr(self):
        ans = f"""Task: {self.task}
        \rPom ID: {self.pom_id}
        \rTag: {self.tag}
        \rGoal: {self.goal}
        \rPomodorro Length: {self.length//60}
        \rRest Length: {self.rest//60}
        \rActive: {self.active}
        \rCompleted: {self.completed}
        \rStart Time: {self.start_time}
        \rEnd Time: {self.end_time}
        \rTime Spent: {self.time_spent}
        \rHistoric Tag: {self.historic_tag}
        \rDue: {self.due}
        \rExpired: {self.expired}"""

        self.assertEqual(self.p.__repr__(), ans)
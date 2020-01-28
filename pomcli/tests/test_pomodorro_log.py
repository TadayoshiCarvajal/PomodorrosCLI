import unittest
from pomcli.app.pomodorro_log import PomodorroLog
from pomcli.app.task_log import TaskLog
from datetime import datetime
from pomcli.app.pomodorro import Pomodorro
from pomcli.app.model import Model
import sqlite3
import os
import sys

class TestPomodorroLog(unittest.TestCase):

    def setUp(self):
        
        self.tasks = [
            [1, "Task 1", "daily", 5, 25, 5, "", False, False],
            [2, "Task 2", "daily", 5, 25, 5, "", False, False],
            [3, "Task 3", "daily", 5, 25, 5, "", False, False],
            [4, "Task 4", "daily", 5, 25, 5, "", False, False],
            [5, "Task 5", "daily", 5, 25, 5, "", False, False],
        ]

        self.pomodorros = [
            [1, "Pom 1", 1, 5, 25, 5, "goal 1", False, False, datetime.now(), datetime.now(), 10, None, False, datetime.now()],
            [2, "Pom 2", 1, 5, 25, 5, "goal 2", False, False, datetime.now(), datetime.now(), 10, None, False, datetime.now()],
            [3, "Pom 3", 2, 5, 25, 5, "goal 3", False, False, datetime.now(), datetime.now(), 10, None, False, datetime.now()],
            [4, "Pom 4", 2, 5, 25, 5, "goal 4", False, False, datetime.now(), datetime.now(), 10, None, False, datetime.now()],
            [5, "Pom 5", 2, 5, 25, 5, "goal 5", False, False, datetime.now(), datetime.now(), 10, None, False, datetime.now()],
        ]    
        
        test_db_path = os.path.dirname(os.path.realpath(sys.argv[0])) + '/test.db'
        conn = sqlite3.connect(test_db_path)
        self.model = Model(conn)
        self.settings = None
        self.tl = TaskLog(self.tasks, self.model, self.settings)
        self.pl = PomodorroLog(self.pomodorros, self.model, self.settings, self.tl)

    def test_constructor(self):
        self.assertEqual(self.pl[1].tag, "Pom 1")
        self.assertEqual(self.pl["Pom 1"].pom_id, 1)
        self.assertEqual(len(self.pl), len(self.pomodorros)*2) # cached under id and name

    def test_get_pomodorro(self):
        pom_id = 1
        tag = "do laundry"
        priority = 5
        task = "Task 1"
        length = 25
        rest = 5
        goal = "separate darks, whites, and colors. Put first load in."
        active = False
        completed = True
        start_time = str(datetime.now())
        end_time = str(datetime.now())
        time_spent = 1000
        historic_tag = None
        expired = False
        due = datetime.now()

        p1 = Pomodorro(pom_id, tag, task, priority, length, rest, goal, 
                        active, completed, start_time, end_time, 
                        time_spent, historic_tag, expired, due)

        pom = [pom_id, tag, task, length, rest, goal, active, completed, 
                 start_time, end_time, time_spent, historic_tag, expired, due]
        
        p2 = self.pl.get_pomodorro(pom)

        self.assertEqual(p1.pom_id, p2.pom_id)
        self.assertEqual(p1.tag, p2.tag)
        self.assertEqual(p1.priority, p2.priority)
        self.assertEqual(p1.task, p2.task)
        self.assertEqual(p1.length, p2.length)
        self.assertEqual(p1.rest, p2.rest)
        self.assertEqual(p1.goal, p2.goal)
        self.assertEqual(p1.active, p2.active)
        self.assertEqual(p1.completed, p2.completed)
        self.assertEqual(p1.start_time, p2.start_time)
        self.assertEqual(p1.end_time, p2.end_time)
        self.assertEqual(p1.time_spent, p2.time_spent)
        self.assertEqual(p1.historic_tag, p2.historic_tag)
        self.assertEqual(p1.expired, p2.expired)
        self.assertEqual(p1.due, p2.due)

    def test_add(self):
        self.pl.add('Task 1', ['tag=test'])
        self.pl = self.model.get_pomodorro_log(self.settings, self.tl)

        self.assertTrue("test" in self.pl.log)

    def test_delete(self):
        self.pl = self.model.get_pomodorro_log(self.settings, self.tl)
        self.pl.delete("Task 1", ["test"])
        self.pl = self.model.get_pomodorro_log(self.settings, self.tl)

        self.assertTrue("test" not in self.pl.log)

    
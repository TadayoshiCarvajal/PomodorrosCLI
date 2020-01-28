import unittest
import sys
from pomcli.app.model import Model
import sqlite3

class TestModel(unittest.TestCase):

    def setUp(self):
        conn = sqlite3.connect('pomcli/tests/test.db')
        c = conn.cursor()

        q1 = f"""INSERT INTO 
                    task (task_id, name, repeats, priority, pomodorro_length, rest_length, 
                    refresh_frequency, completed, pomodorro_complete)
                VALUES  
                    (1, 'task0', 'daily', 1, 1, 1, "", 0, 0),
                    (2, 'task1', 'daily', 1, 2, 1, "", 0, 0),
                    (3, 'task2', 'daily', 1, 3, 1, "", 0, 0),
                    (4, 'task3', 'daily', 1, 4, 1, "", 0, 0),
                    (5, 'task4', 'daily', 1, 5, 1, "", 0, 0),
                    (6, 'task5', 'daily', 1, 6, 1, "", 0, 0),
                    (7, 'task6', 'daily', 1, 7, 1, "", 0, 0),
                    (8, 'task7', 'daily', 1, 8, 1, "", 0, 0),
                    (9, 'task8', 'daily', 1, 9, 1, "", 0, 0),
                    (10, 'task9', 'daily', 1, 10, 1, "", 0, 0);"""

        q2 = f"""INSERT INTO 
                    pomodorro (tag, task_id, length, rest, goal, active, completed, due)
                VALUES  
                    ('pom0', 1, 5, 1, "pom0 goal", 1, 0, NULL),
                    ('pom1', 2, 5, 1, "pom1 goal", 0, 1, NULL),
                    ('pom2', 3, 5, 1, "pom2 goal", 0, 0, NULL),
                    ('pom3', 4, 5, 1, "pom3 goal", 0, 0, NULL),
                    ('pom4', 5, 5, 1, "pom4 goal", 0, 0, NULL),
                    ('pom5', 6, 5, 1, "pom5 goal", 0, 0, NULL),
                    ('pom6', 7, 5, 1, "pom6 goal", 0, 0, NULL),
                    ('pom7', 8, 5, 1, "pom7 goal", 0, 0, NULL),
                    ('pom8', 9, 5, 1, "pom8 goal", 0, 0, NULL),
                    ('pom9', 10, 5, 1, "pom9 goal", 0, 0, NULL);"""
        c.execute(q1)
        c.execute(q2)
        conn.commit()
        self.model = Model(conn)

    def tearDown(self):
        """ This is called after every test case and clears the pomodorro and task tables. """

        conn = sqlite3.connect('pomcli/tests/test.db')
        c = conn.cursor()
        q1 = f""" DELETE FROM task """
        q2 = f""" DELETE FROM pomodorro """
        c.execute(q1)
        c.execute(q2)
        conn.commit()

    def test_get_settings(self):
        """ Tests out the get_settings() method of the Model class. """
        settings = self.model.get_settings()
        pomodorro_length = settings.pomodorro_length
        rest_length = settings.rest_length
        column_width = settings.column_width
        hide_success = settings.hide_success

        self.assertEqual(pomodorro_length, 25)
        self.assertEqual(rest_length, 5)
        self.assertEqual(column_width, 13)
        self.assertFalse(hide_success)

    def test_get_task_log(self):
        """ Tests out the get_task_log() method of the Model class. """
        task_log = self.model.get_task_log(self.model.get_settings())

        t1 = task_log.log['task0']
        t2 = task_log.log[t1.task_id]
        self.assertEqual(t1.repeats, 'daily')
        self.assertEqual(t2, t1)

    def test_get_pomodorro_log(self):
        """ Tests out the get_pomodorro_log() method of the Model class. """
        settings = self.model.get_settings()
        task_log = self.model.get_task_log(settings)
        pomodorro_log = self.model.get_pomodorro_log(settings, task_log)

        p1 = pomodorro_log.log['pom0']
        p2 = pomodorro_log.log[p1.pom_id]
        self.assertEqual(p1.length, 5)
        self.assertEqual(p1, p2)

    def test_settings_set(self):
        """ Tests out the settings_set() method of the Model class. """
        self.model.settings_set('pomodorro_length', 30)
        self.model.settings_set('rest_length', 30)
        self.model.settings_set('column_width', 30)
        self.model.settings_set('hide_success', True)

        settings = self.model.get_settings()
        pomodorro_length = settings.pomodorro_length
        rest_length = settings.rest_length
        column_width = settings.column_width
        hide_success = settings.hide_success

        self.assertEqual(pomodorro_length, 30)
        self.assertEqual(rest_length, 30)
        self.assertEqual(column_width, 30)
        self.assertTrue(hide_success)

        self.model.settings_set('pomodorro_length', 25)
        self.model.settings_set('rest_length', 5)
        self.model.settings_set('column_width', 13)
        self.model.settings_set('hide_success', False)

    def test_add_task(self):
        """ Tests out the add_task() method of the Model class. """

        task_name = "test task add"
        repeats = "daily"
        priority = 10
        pomodorro_length = 60
        rest_length = 25

        self.model.add_task(task_name, repeats, priority, pomodorro_length, rest_length)

        settings = self.model.get_settings()
        task_log = self.model.get_task_log(settings)

        self.assertTrue('test task add' in task_log.log)
        test_task = task_log.log['test task add']

        self.assertEqual(repeats, test_task.repeats)
        self.assertEqual(priority, test_task.priority)
        self.assertEqual(pomodorro_length, test_task.pomodorro_length)
        self.assertEqual(rest_length, test_task.rest_length)

    def test_delete_task(self):
        """ Tests out the delete_task() method of the Model class. """

        self.model.delete_task(1) # should delete task0 from task_log

        settings = self.model.get_settings()
        task_log = self.model.get_task_log(settings)

        self.assertTrue('task0' not in task_log.log)
        self.assertTrue('task1' in task_log.log)

    def test_edit_task(self):
        """ Tests out the edit_task() method of the Model class. """

        task_id = 1
        new_name = 'Test Task Edit'
        new_repeats = 'weekly'
        new_priority = 10
        new_pomodorro_length = 60
        new_rest_length = 10
        new_pomodorro_complete = False
        
        self.model.edit_task(
            task_id, new_name, new_repeats, new_priority, 
            new_pomodorro_length, new_rest_length, new_pomodorro_complete
        )

        settings = self.model.get_settings()
        task_log = self.model.get_task_log(settings)
        test_task = task_log.log[1]

        self.assertEqual(new_name, test_task.name)
        self.assertEqual(new_repeats, test_task.repeats)
        self.assertEqual(new_priority, test_task.priority)
        self.assertEqual(new_pomodorro_length, test_task.pomodorro_length)
        self.assertEqual(new_rest_length, test_task.rest_length)
        self.assertFalse(new_pomodorro_complete)

    def test_add_pomodorro(self):
        """ Tests out the add_pomodorro() method of the Model class. """
        from datetime import datetime

        task_id = 1
        tag = 'Test Add Pomodorro'
        length = 25
        rest = 5
        goal = "Tests the add pomodorro method."
        due = datetime.now()

        self.model.add_pomodorro(task_id, tag, length, rest, goal, due)

        settings = self.model.get_settings()
        task_log = self.model.get_task_log(settings)
        pom_log = self.model.get_pomodorro_log(settings, task_log)

        self.assertTrue(tag in pom_log.log)

        test_pom = pom_log.log[tag]

        self.assertEqual(length, test_pom.length)
        self.assertEqual(rest, test_pom.rest)
        self.assertEqual(goal, test_pom.goal)
        self.assertEqual(str(due), test_pom.due)

    def test_delete_pomodorro(self):
        """ Tests out the delete_pomodorro() method of the Model class. """

        settings = self.model.get_settings()
        task_log = self.model.get_task_log(settings)
        pom_log = self.model.get_pomodorro_log(settings, task_log)

        test_pom = pom_log.log['pom0']
        task_id = task_log.log[test_pom.task].task_id
        pom_id = test_pom.pom_id

        self.model.delete_pomodorro(task_id, pom_id)

        pom_log = self.model.get_pomodorro_log(settings, task_log)

        self.assertTrue('pom0' not in pom_log.log)

    def test_change_tag(self):
        """ Tests out the change_tag() method of the Model class. """

        settings = self.model.get_settings()
        task_log = self.model.get_task_log(settings)
        pom_log = self.model.get_pomodorro_log(settings, task_log)

        test_pom = pom_log.log['pom0']
        pom_id = test_pom.pom_id

        self.model.change_tag(pom_id, "TEST TAG")

        pom_log = self.model.get_pomodorro_log(settings, task_log)

        self.assertEqual("TEST TAG", pom_log.log[pom_id].tag)

    def test_change_goal(self):
        """ Tests out the change_goal() method of the Model class. """

        settings = self.model.get_settings()
        task_log = self.model.get_task_log(settings)
        pom_log = self.model.get_pomodorro_log(settings, task_log)

        test_pom = pom_log.log['pom0']
        task_id = task_log.log[test_pom.task].task_id
        pom_id = test_pom.pom_id

        self.model.change_goal(pom_id, "THIS IS THE NEW GOAL")

        pom_log = self.model.get_pomodorro_log(settings, task_log)

        self.assertEqual("THIS IS THE NEW GOAL", pom_log.log[pom_id].goal)

    def test_edit_pomodorro(self):
        """ Tests out the edit_pomodorro() method of the Model class. """

        from datetime import datetime
        settings = self.model.get_settings()
        task_log = self.model.get_task_log(settings)
        pom_log = self.model.get_pomodorro_log(settings, task_log)
        test_pom = pom_log.log['pom0']
        task_id = task_log.log[test_pom.task].task_id
        
        pom_id = test_pom.pom_id
        new_tag = "NEW TAG"
        new_goal = "NEW GOAL"
        new_length = 100
        new_rest = 50
        new_due = datetime.now()

        self.model.edit_pomodorro(pom_id, new_tag, new_goal, new_length, new_rest, new_due)

        pom_log = self.model.get_pomodorro_log(settings, task_log)
        pom = pom_log.log[pom_id]
        
        self.assertEqual(new_tag, pom.tag)
        self.assertEqual(new_goal, pom.goal)
        self.assertEqual(new_length, pom.length)
        self.assertEqual(new_rest, pom.rest)
        self.assertEqual(str(new_due), pom.due)

    def test_get_active_pomodorro(self):
        """ Tests out the get_active_pomodorro() method of the Model class. """

        settings = self.model.get_settings()
        task_log = self.model.get_task_log(settings)
        pom_log = self.model.get_pomodorro_log(settings, task_log)

        active_pom = self.model.get_active_pomodorro()
        
        self.assertEqual(active_pom[1], 'pom0')

    def test_is_complete(self):
        """ Tests out the is_complete() method of the Model class. """

        settings = self.model.get_settings()
        task_log = self.model.get_task_log(settings)
        pom_log = self.model.get_pomodorro_log(settings, task_log)

        test_pom0 = pom_log.log['pom0']
        pom_id0 = test_pom0.pom_id

        test_pom1 = pom_log.log['pom1']
        pom_id1 = test_pom1.pom_id

        complete0 = self.model.is_complete(pom_id0)
        complete1 = self.model.is_complete(pom_id1)

        self.assertEqual(complete0, 0)
        self.assertEqual(complete1, 1)

    def test_set_active_pomodorro(self):
        """ Tests out the set_active_pomodorro() method of the Model class. """

        settings = self.model.get_settings()
        task_log = self.model.get_task_log(settings)
        pom_log = self.model.get_pomodorro_log(settings, task_log)

        test_pom = pom_log.log['pom1']

        self.model.set_active_pomodorro(test_pom)

        pom_log = self.model.get_pomodorro_log(settings, task_log)
        test_pom = pom_log.log['pom1']

        self.assertEqual(test_pom.active, 1)

    def test_begin_pomodorro(self):
        """ Tests out the begin_pomodorro() method of the Model class. """
        
        from time import time
        settings = self.model.get_settings()
        task_log = self.model.get_task_log(settings)
        pom_log = self.model.get_pomodorro_log(settings, task_log)

        test_pom = pom_log.log['pom0']
        start_time = time()
        self.assertTrue(test_pom.start_time is None)

        self.model.begin_pomodorro(test_pom, start_time)
    
        pom_log = self.model.get_pomodorro_log(settings, task_log)
        test_pom = pom_log.log['pom0']

        self.assertTrue(test_pom.start_time is not None)

    def test_reset_pomodorro(self):
        """ Tests out the reset_pomodorro() method of the Model class. """
        
        settings = self.model.get_settings()
        task_log = self.model.get_task_log(settings)
        pom_log = self.model.get_pomodorro_log(settings, task_log)

        test_pom = pom_log.log['pom0']

        self.model.reset_pomodorro(test_pom)
    
        pom_log = self.model.get_pomodorro_log(settings, task_log)
        test_pom = pom_log.log['pom0']

        self.assertEqual(test_pom.active, 0)

    def test_complete_pomodorro(self):
        """ Tests out the complete_pomodorro() method of the Model class. """
        
        from time import time
        settings = self.model.get_settings()
        task_log = self.model.get_task_log(settings)
        pom_log = self.model.get_pomodorro_log(settings, task_log)
        test_pom = pom_log.log['pom0']
        pom_id = test_pom.pom_id

        self.model.complete_pomodorro(test_pom, time(), time(), 1)
    
        pom_log = self.model.get_pomodorro_log(settings, task_log)
        test_pom = pom_log.log[pom_id]

        self.assertEqual(test_pom.completed, 1)

    def test_complete_task(self):
        """ Tests out the complete_task() method of the Model class. """
        
        settings = self.model.get_settings()
        task_log = self.model.get_task_log(settings)
        test_task = task_log.log['task0']
        task_id = test_task.task_id

        self.model.complete_task(task_id)
    
        task_log = self.model.get_task_log(settings)
        test_task = task_log.log['task0']

        self.assertEqual(test_task.completed, 1)

    def test_expire_pomodorro(self):
        """ Tests out the expire_pomodorro() method of the Model class. """
        
        settings = self.model.get_settings()
        task_log = self.model.get_task_log(settings)
        pom_log = self.model.get_pomodorro_log(settings, task_log)
        test_pom = pom_log.log['pom0']
        task_id = task_log.log[test_pom.task].task_id
        pom_id = test_pom.pom_id

        self.model.expire_pomodorro(test_pom, task_id, pom_log)
    
        pom_log = self.model.get_pomodorro_log(settings, task_log)
        test_pom = pom_log.log[pom_id]

        self.assertEqual(test_pom.expired, 1)

    def test_edit_pomodorro_due(self):
        """ Tests out the edit_pomodorro_due() method of the Model class. """
        from datetime import datetime

        settings = self.model.get_settings()
        task_log = self.model.get_task_log(settings)
        test_task = task_log.log['task0']
        task_id = test_task.task_id
        pom_log = self.model.get_pomodorro_log(settings, task_log)
        new_due = datetime.now()

        self.model.edit_pomodorro_due(task_id, new_due)
    
        pom_log = self.model.get_pomodorro_log(settings, task_log)
        test_pom = pom_log.log['pom0']

        self.assertEqual(str(new_due), test_pom.due)

    def test_epoch_to_local(self):
        """ Tests out the epoch_to_local() method of the Model class. """
        
        from time import time
        time = self.model.epoch_to_local(time())
        date, time = time.split()
        date = date.split('-')
        time = time.split(':')
        datetime = list(map(int, date + time))
        self.assertEqual(len(datetime), 6)
class Model:
    def __init__(self, conn):
        self.conn = conn 
        self.c = conn.cursor()

    def initialize_tables(self):
        """ Used in the initial setup to create the tables used in this application.
        
        Creates three tables: settings, tasks, and pomodorros. Settings contains a
        single row, with name = main. These are the user settings."""

        self.c.execute(
            """ CREATE TABLE settings(
                name TEXT,
                pomodorro_length INTEGER,
                rest_length INTEGER,
                column_width INTEGER,
                hide_success INTEGER DEFAULT 0);""")
        
        self.c.execute(
            """ INSERT INTO settings (name, pomodorro_length, rest_length, column_width)
                VALUES ('main', 25, 5, 13);""")

        self.c.execute(
            """ CREATE TABLE task(
                task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                repeats TEXT,
                priority INTEGER DEFAULT 5,
                pomodorro_length INTEGER,
                rest_length INTEGER,
                refresh_frequency TEXT,
                completed INTEGER DEFAULT 0,
                pomodorro_complete DEFAULT 0);""")

        self.c.execute(
            """ CREATE TABLE pomodorro(
                pom_id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag TEXT DEFAULT NULL,
                task_id INTEGER,
                length INTEGER,
                rest INTEGER,
                goal BLOB DEFAULT NULL,
                active INTEGER DEFAULT 0,
                completed INTEGER DEFAULT 0,
                start_time TEXT DEFAULT NULL,
                end_time TEXT DEFAULT NULL,
                time_spent INTEGER DEFAULT 0,
                historic_tag TEXT DEFAULT NULL,
                expired INTEGER DEFAULT 0,
                due TEXT);""")

        self.conn.commit()

    def get_settings(self):
        """ Fetches the user settings from the database."""

        from .settings import Settings
        self.c.execute(
            """ SELECT pomodorro_length, rest_length, column_width, hide_success
                FROM settings
                WHERE name = 'main'""")
        
        vals = self.c.fetchone()
        args = {"pomodorro_length" : vals[0],
                "rest_length" : vals[1],
                "column_width" : vals[2],
                "hide_success" : vals[3]}
        return Settings(args, self)

    def get_pomodorro_log(self, settings, task_log):
        """ Returns a PomodorroLog object.

        Queries the database to access the pomodorros, constructs
        a PomodorroLog using those pomodorros, and returns it."""

        from .pomodorro_log import PomodorroLog

        self.c.execute(
            """ SELECT *
                FROM pomodorro;""")

        pomodorros = self.c.fetchall()
        pomodorro_log = PomodorroLog(pomodorros, self, settings, task_log)
        return pomodorro_log
        
    def get_task_log(self, settings):
        """ Returns a TaskLog object.

        Queries the database to access the tasks, constructs
        a TaskLog using those pomodorros, and then returns it."""

        from .task_log import TaskLog

        self.c.execute("""SELECT * 
                          FROM task""")
        tasks = self.c.fetchall()
        task_log = TaskLog(tasks, self, settings)
        return task_log
    
    def settings_set(self, attribute, value):
        """ Modifies the user settings.
        
        Takes a settings attribute and value and updates that attribute
        in the settings to the new value."""

        q = f"""UPDATE settings 
                SET {attribute} = {value}
                WHERE name = 'main'"""
        self.c.execute(q)
        self.conn.commit()

    def add_task(self, task_name, repeats, priority, pomodorro_length, rest_length):
        """ Adds a new row to the task table."""

        q = f"""INSERT INTO task (name, repeats, priority, pomodorro_length, rest_length)
                VALUES ( '{task_name}', '{repeats}', {priority}, {pomodorro_length}, {rest_length});"""
        self.c.execute(q)
        self.conn.commit()

    def delete_task(self, task_id):
        """ Removes a row from the task table.
        
        Deletes a row from the task table and deletes all of the 
        pomodorros in the pomodorro table associated with that task."""

        q1 = f"""DELETE FROM task
                 WHERE task_id = {task_id}"""
        q2 = f"""DELETE FROM pomodorro
                 WHERE task_id = {task_id}"""
        self.c.execute(q1)
        self.c.execute(q2)
        self.conn.commit()

    def edit_task(self, task_id, new_name, new_repeats, new_priority, 
            new_pomodorro_length, new_rest_length, new_pomodorro_complete):
        """ Updates the values of a task with the new information."""

        q = f"""UPDATE task
                SET name = '{new_name}',
                    repeats = '{new_repeats}',
                    priority = {new_priority},
                    pomodorro_length = {new_pomodorro_length},
                    rest_length = {new_rest_length},
                    pomodorro_complete = {new_pomodorro_complete}
                WHERE task_id = {task_id}"""
        self.c.execute(q)
        self.conn.commit()

    def add_pomodorro(self, task_id, tag, length, rest, goal, due):
        """ Adds a row to the pomodorro table."""
        import datetime
        #due = datetime.datetime.now()
        if tag:
            q = f"""INSERT INTO pomodorro (tag, task_id, length, rest, goal, due)
                    VALUES ( '{tag}', '{task_id}', {length}, {rest}, '{goal}', '{due}');"""
        else:
            q = f"""INSERT INTO pomodorro (task_id, length, rest, goal, due)
                    VALUES ( '{task_id}', {length}, {rest}, '{goal}', '{due}');"""
        self.c.execute(q)
        self.conn.commit()

    def delete_pomodorro(self, task_id, pom_id):
        """ Deletes a row from the pomodorro table."""

        q = f"""DELETE FROM pomodorro
                 WHERE pom_id={pom_id}"""

        self.c.execute(q)
        self.conn.commit()

    def change_tag(self, pom_id, new_tag):
        """ Changes the tag attribute of a pomodorro in the pomodorro table."""

        q = f"""UPDATE pomodorro
                SET tag = '{new_tag}'
                WHERE pom_id = {pom_id}"""
                
        self.c.execute(q)
        self.conn.commit()

    def change_goal(self, pom_id, new_goal):
        """ Changes the goal attribute of a pomodorro in the pomodorro table."""

        q = f"""UPDATE pomodorro
                SET goal = '{new_goal}'
                WHERE pom_id = {pom_id}"""
        self.c.execute(q)
        self.conn.commit()

    def edit_pomodorro(self, pom_id, new_tag, new_goal, new_length, new_rest, new_due):
        """ Updates the values of a task with the new information."""

        q = f"""UPDATE pomodorro
                SET tag = '{new_tag}',
                    goal = '{new_goal}',
                    length = {new_length},
                    rest = {new_rest},
                    due = '{new_due}'
                WHERE pom_id = {pom_id}"""
        self.c.execute(q)
        self.conn.commit()

    def get_active_pomodorro(self):
        """ Fetches the active pomodorro if there is one, othewise returns None."""

        q = f"""SELECT *
                FROM pomodorro
                WHERE active = 1;"""
        self.c.execute(q)
        active_pomodorro = self.c.fetchone()

        if not active_pomodorro: return None
        return active_pomodorro

    def is_complete(self, pom_id):
        """ Returns the completed value of a pomodorro."""

        q = f"""SELECT completed
                FROM pomodorro
                WHERE pom_id = {pom_id};"""
        self.c.execute(q)
        is_complete = self.c.fetchone()[0]
        return is_complete

    def set_active_pomodorro(self, pomodorro):
        """ Sets the specified pomodorro to active."""

        pom_id = pomodorro.pom_id
        q = f"""UPDATE pomodorro
                SET active = 1
                WHERE pom_id = {pom_id}"""
        self.c.execute(q)
        self.conn.commit()

    def begin_pomodorro(self, pomodorro, time):
        """ Updates the start_time of the initiated pomodorro."""

        pom_id = pomodorro.pom_id
        time = self.epoch_to_local(time)
        q = f"""UPDATE pomodorro
                SET start_time = '{time}'
                WHERE pom_id = {pom_id}"""
        self.c.execute(q)
        self.conn.commit()

    def reset_pomodorro(self, pomodorro):
        """ Resets the pomodorro's timer information to the default values."""

        pom_id = pomodorro.pom_id
        q = f"""UPDATE pomodorro
                SET active = 0,
                    start_time = NULL,
                    end_time = NULL,
                    time_spent = 0
                WHERE pom_id = {pom_id}"""
        self.c.execute(q)
        self.conn.commit()

    def complete_pomodorro(self, pomodorro, start_time, end_time, time_spent):
        """ Updates the attributes of the completed pomodorro.
        
        When a pomodorro is completed, we store the amount of time it took to complete
        the pomodorro and when it started and ended. We mark it complete and remove
        the tag so the tag may be used by future pomodorros. We store the tag in the 
        historic_tag parameter so we can search completed pomodorros by their tags."""

        pom_id = pomodorro.pom_id
        historic_tag = pomodorro.tag
        start_time = self.epoch_to_local(start_time)
        end_time = self.epoch_to_local(end_time)
        q = f"""UPDATE pomodorro
                SET active = 0,
                    start_time = '{start_time}',
                    end_time = '{end_time}',
                    time_spent = {time_spent},
                    completed = 1,
                    tag = NULL,
                    historic_tag = '{historic_tag}'
                WHERE pom_id = {pom_id}"""
        self.c.execute(q)
        self.conn.commit()

    def complete_task(self, task_id):
        """ If a task has repeats=once and pomodorro_complete=True,
        this method marks the task completed if there are no more 
        pomodorros remaining."""
        q = f"""UPDATE task
                SET completed = 1
                WHERE task_id = {task_id}"""
        self.c.execute(q)
        self.conn.commit()

    def expire_pomodorro(self, pomodorro, task_id, pomodorro_log):
        """ Marks a pomodorro expired and replaces it with a new pomodorro. """
        q = f"""UPDATE pomodorro
                SET tag = NULL,
                    historic_tag = '{pomodorro.tag}',
                    expired = 1
                WHERE pom_id = {pomodorro.pom_id}"""

        self.c.execute(q)
        self.conn.commit()

        tag = pomodorro.tag
        goal = pomodorro.goal
        length = pomodorro.length // 60
        rest = pomodorro.rest // 60
        options = []
        if tag:
            options.append(f"tag={tag}")
        if goal:
            options.append(f"goal={goal}")
        options.append(f"pomodorro_length={length}")
        options.append(f"rest_length={rest}")
        pomodorro_log.add(task_id, options)

    def edit_pomodorro_due(self, task_id, new_due):
        """ Updates the values of a task with the new information."""

        q = f"""UPDATE pomodorro
                SET due = '{new_due}'
                WHERE task_id = {task_id} 
                AND expired != 1 
                AND completed != 1"""

        self.c.execute(q)
        self.conn.commit()

    def epoch_to_local(self, epoch_time):
        """ Converts the given epoch time to year-month-day hour:min:sec format.
        
        Time is passed to this function from the time.time() function. This helper
        function converts that time to a more user-friendly format."""
        
        import time
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch_time))
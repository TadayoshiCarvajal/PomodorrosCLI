from .pomodorro import Pomodorro

class Task:
    def __init__(self, task_id, name, repeats, 
                last_refresh, next_refresh, deleted, completed):
        """ An object representing a real world task.

        task_id - int - the unique id of this task
        name - str - the name of the task.
        repeats - str - once, daily, weekly, monthly, or yearly.
        pomodorro_count - int - the number of pomodorros this task gets.
        """
        self.task_id = task_id
        self.name = name
        self.repeats = repeats
        self.last_refresh = last_refresh
        self.next_refresh = next_refresh
        self.deleted = deleted
        self.completed = completed

    def show(self, brief=False):
        """Displays the information belonging to this task."""
        if not brief:
            print(self.__repr__())
        else:
            task_id = str(self.task_id)
            name = self.name
            print(f"{name:s}({task_id:s})")
        
    def __repr__(self):
        s = \
        f"""Task ID: {self.task_id}
        \rName: {self.name}
        \rRepeats: {self.repeats}
        """
        return s

    def __str__(self, settings):
        cw = settings.column_width
        task_id = str(self.task_id)
        name = self.name
        repeats = self.repeats
        s = f"{task_id:^{cw}s}|{name:^{cw}s}|{repeats:^{cw}s}"
        return s
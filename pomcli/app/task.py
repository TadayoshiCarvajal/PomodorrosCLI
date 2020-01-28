from .pomodorro import Pomodorro

class Task:
    def __init__(self, task_id, name, repeats, priority,
                pomodorro_length, rest_length, refresh_frequency, 
                completed, pomodorro_complete):
        """ An object representing a real world task.

        task_id - int - the unique id of this task
        name - str - the name of the task.
        repeats - str - once, daily, weekly, monthly, or yearly.
        pomodorro_count - int - the number of pomodorros this task gets.
        """
        self.task_id = task_id
        self.name = name
        self.repeats = repeats
        self.priority = priority
        self.pomodorro_length = pomodorro_length
        self.rest_length = rest_length
        self.refresh_frequency = refresh_frequency
        self.completed = bool(completed)
        self.pomodorro_complete = pomodorro_complete

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
        \rPriority: {self.priority}
        \rRepeats: {self.repeats}
        \rFrequency: {self.refresh_frequency}
        \rDefault Pomodorro Length: {self.pomodorro_length}
        \rDefault Rest Length: {self.rest_length}
        \rComplete With Pomodorro: {self.pomodorro_complete}
        \rCompleted: {self.completed}
        """
        return s

    def __str__(self, settings):
        cw = settings.column_width
        task_id = str(self.task_id)
        name = self.name
        repeats = self.repeats
        priority = self.priority
        pom_length = self.pomodorro_length
        rest_length = self.rest_length
        s = f"{task_id:^{cw}s}|{name:^{cw}s}|{repeats:^{cw}s}|{priority:^{cw}d}|{pom_length:^{cw}d}|{rest_length:^{cw}d}"
        return s
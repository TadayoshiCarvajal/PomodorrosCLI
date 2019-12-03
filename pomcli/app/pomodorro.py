from datetime import datetime

class Pomodorro:
    """An object that represents a pomodorro.

    A pomodorro is a window of time consisting of two parts: a work phase,
    and a rest phase. Every pomodorro belongs to a task. In the work phase
    the user diligently works for a prespecified period of time on that task
    and in the rest phase that follows the work phase, the user takes a break."""
    def __init__(self, pom_id, tag, task_id, length, rest, goal, 
                        active, completed, start_time, end_time, 
                        time_spent, historic_tag):
        """
        pom_id - int - the integer ID of the pomodorro.
        tag - str/None - the tag of the pomodorro if it exists, else None.
        task_id - Task - the task to which this pomodorro belongs
        length - int - the length of this pomodorro in seconds
        rest - int - the length of the rest phase in seconds
        goal - str - a string summarizing the goal for this pomodorro
        active - bool - True if this pomodorro is the active pomodorro else False
        completed - bool - True if the pomodorro is completed else False
        start_time - datetime - the time that we last begin/unpause this pomodorro
        end_time - datetime - the time that we complete this pomodorro
        time_spent - datetime.timedelta - the amount of time spent on the pomodorro
        historic_tag - str - the tag a completed pomodorro had prior to completion.
        """
        self.pom_id = pom_id
        self.tag = tag
        self.task = task_id
        self.length = length
        self.rest = rest
        self.goal = goal
        self.active = bool(active)
        self.completed = bool(completed)
        self.start_time = start_time
        self.end_time = end_time
        self.time_spent = time_spent
        self.historic_tag = historic_tag

    def show(self, brief=False):
        """ Display the pomodorro information. """
        if brief:
            print(f"{self.task:s} - {self.goal:s}")
        else:
            print(self.__repr__())    

    def __repr__(self):
        s = \
        f"""Task: {self.task}
        \rPom ID: {self.pom_id}
        \rTag: {self.tag}
        \rGoal: {self.goal}
        \rActive: {self.active}
        \rCompleted: {self.completed}
        \rStart Time: {self.start_time}
        \rEnd Time: {self.end_time}
        \rTime Spent: {self.time_spent}
        \rHistoric Tag: {self.historic_tag}"""

        return s

    def __str__(self, settings, history=False):
        cw = settings.column_width
        task = str(self.task)
        pom_id = str(self.pom_id)
        s = f"{task:^{cw}s}|{pom_id:^{cw}s}"
        if not history and self.tag:
            s += f"|{self.tag:^{cw}s}"
        elif history and self.historic_tag:
            s += f"|{self.historic_tag:^{cw}s}"
        if self.goal:
            s += f"|{self.goal:^{cw}s}"
        return s
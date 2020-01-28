class RecurrenceManager:
    def __init__(self, pomodorro_log, task_log, model):
        """ """
        
        self.pomodorro_log = pomodorro_log

        self.task_log = task_log

        self.model = model

    def update_pomodorros(self):
        import datetime
        """ Update the pomodorros.
        
        Checks the next_refresh value for each pomodorro, compares it to the current time.
        If the current time is >=, then refresh_frequency is used to determine the new
        value of next_refresh. The former pomodorro is marked expired. A new pomodorro is 
        generated with the new next_refresh value."""

        now = datetime.datetime.now()
        #print('now:', now)
        for pom_id in self.pomodorro_log.ids:
            pomodorro = self.pomodorro_log.log[pom_id]
            if not pomodorro.expired and not pomodorro.completed:
                task_id = pomodorro.task
                task = self.task_log.log[task_id]
                if task.repeats != 'once': # this pomodorro is repeating
                    due = datetime.datetime.strptime(pomodorro.due, '%Y-%m-%d %H:%M:%S.%f')
                    #print(due)
                    if now > due: # pomodorro is expired
                        self.model.expire_pomodorro(pomodorro, task.task_id, self.pomodorro_log)
                        #print('Replaced!')
        #print('~~~~~~~~~~~~~')

    def update_edited_task(self, task_id, new_repeats):
        """ Updates the pomodorros belonging to a task which has been edited from 
        repeats != once to repeats = once OR repeats = once to repeats != once."""

        task_id = self.task_log.log[task_id].task_id
        new_due = self.pomodorro_log.get_due(new_repeats)
        self.model.edit_pomodorro_due(task_id, new_due)
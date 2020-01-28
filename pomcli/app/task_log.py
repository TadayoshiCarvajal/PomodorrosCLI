class TaskLog:
    def __init__(self, tasks, model, settings):
        self.model = model
        self.log = {}
        self.ids = set()
        self.names = set()
        self.generate_tasks(tasks)
        self.settings = settings

    def generate_tasks(self, tasks):
        """ Generates the log, ids, and names fields of the class.
        
        A TaskLog is initialized using a list of tasks queried from the database.
        This list is used by this method to initialize the values of log, ids, and names."""
        
        from .task import Task
        for task in tasks:
            task_id = task[0]
            name = task[1]
            repeats = task[2]
            priority = task[3]
            pomodorro_length = task[4]
            rest_length = task[5]
            refresh_frequency = task[6]
            completed = task[7]
            pomodorro_complete = bool(task[8])

            task = Task(task_id,
                        name,
                        repeats,
                        priority,
                        pomodorro_length,
                        rest_length,
                        refresh_frequency,
                        completed,
                        pomodorro_complete)
            self.log[task_id] = task
            self.log[name] = task
            self.ids.add(task_id)
            self.names.add(name)

    def show(self, options):
        """ Displays the tasks inside of the TaskLog.
        
        Prints the title, Task Log:, on its own line and then on each subsequent
        line, prints the tasks if there are any."""
        option = None
        if options:
            option = options[0]
        repeating = {"daily", "weekly", "monthly", "yearly"}

        # Display the task log
        print("Task Log:")
        cw = self.settings.column_width
        header = f"{'TaskID':^{cw}s}|{'Name':^{cw}s}|{'Repeats':^{cw}s}|{'Priority':^{cw}s}|{'Length':^{cw}s}|{'Rest':^{cw}s}"
        print(header)
        N = header.count('|') + 1
        print("-"*(N*cw+(N-1))) # controls size of header underlining.
        
        tasks = sorted([self.log[task_id] for task_id in self.ids if not self.log[task_id].completed], key=lambda x: x.priority, reverse=True)
        for task in tasks:
            if option == "once" and task.repeats == "once":
                print(task.__str__(self.settings))
            elif option == "repeating" and task.repeats in repeating:
                print(task.__str__(self.settings))
            elif option is None:
                print(task.__str__(self.settings))

    def add(self, options):
        """ Adds the specified Task to the TaskLog.
        
        Tasks are added by name, and optionally the repeats attribute.
        Tasks can repeat once, daily, weekly, and monthly."""

        options = {option.split('=')[0]:option.split('=')[1] for option in options}

        name = options['name']
        repeats = 'once' if 'repeats' not in options else options['repeats']
        priority = 5 if 'priority' not in options else options['priority']
        pomodorro_length = self.settings.pomodorro_length if 'pomodorro_length' not in options else options['pomodorro_length']
        rest_length = self.settings.rest_length if 'rest_length' not in options else options['rest_length']
        
        self.model.add_task(name, repeats, priority, pomodorro_length, rest_length)
        
    def delete(self, options):
        """ Deletes the specified task.
        
        A task must be specified by either task_id or name. Task deletion also causes 
        all of the task's pomodorros to also be deleted. """

        task_id = options[0]
        if task_id.isdigit():
            task_id = int(task_id)
        elif task_id in self.names:
            task_id = self.log[task_id].task_id
        self.model.delete_task(task_id)

    def show_task(self, task_id, options):
        """ Displays the specified task's information.
        
        A task must be specified by either task_id or name."""
        option = None
        if options:
            option = options[0]

        if task_id.isdigit():
            task_id = int(task_id)
        task = self.log[task_id]
        
        if option == "brief":
            task.show(brief=True)
        else:
            task.show()

    def edit_task(self, task_id, options):
        """ Edits the specified task.
        
        A task must be specified by either task_id or name. The user
        can specify the values to change about a Task with attribute=value
        where attribute it an editable attribute. Name and repeats are editable values. """

        if task_id in self.names:
            task_id = self.log[task_id].task_id
        
        old_repeats = self.log[task_id].repeats
        
        attrs_to_change = {option.split("=")[0]:option.split("=")[1] for option in options}
        new_name = self.log[task_id].name if 'name' not in attrs_to_change else attrs_to_change['name']
        new_repeats = self.log[task_id].repeats if 'repeats' not in attrs_to_change else attrs_to_change['repeats']
        new_priority = self.log[task_id].priority if 'priority' not in attrs_to_change else attrs_to_change['priority']
        new_pomodorro_length = self.log[task_id].pomodorro_length if 'pomodorro_length' not in attrs_to_change \
                                                                    else attrs_to_change['pomodorro_length']
        new_rest_length = self.log[task_id].rest_length if 'rest_length' not in attrs_to_change \
                                                                    else attrs_to_change['rest_length']

        if new_repeats == 'once':
            new_pomodorro_complete = self.log[task_id].pomodorro_complete if 'pomodorro_complete' not in attrs_to_change \
                                                                        else attrs_to_change['pomodorro_complete']
        else: # only repeats='once' can be completed upon final pomodorro completion. 
            new_pomodorro_complete = False

        self.model.edit_task(
            task_id, 
            new_name,
            new_repeats, 
            new_priority, 
            new_pomodorro_length, 
            new_rest_length,
            new_pomodorro_complete)

        if old_repeats != new_repeats:
            return True, new_repeats
        return False, None


    def __getitem__(self, name):
        return self.log[name]

    def __setitem__(self, name, value):
        self.log[name] = value
    
    def __len__(self):
        return len(self.log)
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
            last_refresh = task[3]
            next_refresh = task[4]
            deleted = task[5]
            completed = task[6]

            task = Task(task_id, name, repeats, last_refresh, next_refresh, deleted, completed)
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
        header = f"{'TaskID':^{cw}s}|{'Name':^{cw}s}|{'Repeats':^{cw}s}"
        print(header)
        print("-"*(3*cw+2))
        for task_id in self.ids:
            task = self.log[task_id]
            if not task.deleted:
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

        name = options[0]
        if len(options) == 1: repeats = 'once'
        elif len(options) == 2: repeats = options[1]
        
        self.model.add_task(name, repeats)
        
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
        
        attrs_to_change = {option.split("=")[0]:option.split("=")[1] for option in options}
        new_name = self.log[task_id].name if 'name' not in attrs_to_change else attrs_to_change['name']
        new_repeats = self.log[task_id].repeats if 'repeats' not in attrs_to_change else attrs_to_change['repeats']
        self.model.edit_task(task_id, new_name, new_repeats)

    def __getitem__(self, name):
        return self.log[name]

    def __setitem__(self, name, value):
        self.log[name] = value
    
    def __len__(self):
        return len(self.log)
from .timer import Timer

class Interface:
    def __init__(self, task_log, pomodorro_log, settings, model):
        """ Creates an interface object used to validate the user
        input and then process the command accordingly"""
        from .error_handler import ErrorHandler
        from .recurrence_manager import RecurrenceManager
        
        # User settings
        self.settings = settings
        
        # Interface between ui and database
        self.model = model

        # All task information
        self.task_log = task_log

        # All pomodorro information
        self.pomodorro_log = pomodorro_log

        # Handler of command errors
        self.error_handler = ErrorHandler(settings, model, task_log, pomodorro_log)

        # Handles recurring pomodorros
        self.recurrence_manager = RecurrenceManager(self.pomodorro_log, self.task_log, self.model)


    def process_input(self, s):
        """ Validates and handles inputs.
        
        Inputs are in the form of an array of arguments from the commandline.
        They follow the basic structure <object> <action> <options> if the object
        has no object ID, i.e., is not a task or pomodorro. If an object is a task
        or pomodorro, it has an object ID and commands are:
        <object> <object_id> <action> <options>. 
        
        Inputs that do not follow this structure, or follow this structure, but 
        provide invalid information, are rejected by the ErrorHandler object."""
        s = self.parse_input(s)

        if self.error_handler.valid_input(s):
            self.execute_command(s)
            if not self.settings.hide_success:
                print("Success")

    def parse_input(self, s):
        """ Parses the input array and returns a dictionary containing the values.
        
        This is an intermediate step used to help make sure that commands are in the
        specified format. An alias map contained in the ErrorHandler helps to
        normalize accross various acceptable aliases for objects. """
        if not s:
            return {}
        
        if len(s) >= 1:
            rtn = {}
            alias = self.error_handler.alias
            object = alias[s[0]] if s[0] in alias else s[0]
            rtn["object"] = object
        
            if object in {"pomodorro", "task"}:
                if len(s) >= 2:
                    rtn["object_id"] = s[1]
                if len(s) >= 3:
                    rtn["action"] = s[2]
                    rtn["options"] = s[3:]
            elif object == "timer":
                if len(s) >= 2:
                    rtn["action"] = s[1]
                if len(s) >= 3:
                    rtn["object_id"] = s[2]
                    rtn["options"] = s[3:]
            else:
                if len(s) >= 2:
                    rtn["action"] = s[1]
                    rtn["options"] = s[2:]
            return rtn

    def execute_command(self, args):
        """ Handles valid input.
        
        If the ErrorHandler deems a command valid, the interface uses this method
        to direct the command to the appropriate subroutine."""
        object = args["object"]
        action = args["action"]
        
        if object == 'settings' and action == 'show':
            self.settings_show(args)
        if object == 'settings' and action == 'set':
            self.settings_set(args)
        if object == 'tasklog' and action == 'show':
            self.tasklog_show(args)
        if object == 'tasklog' and action == 'add':
            self.add_task(args)
        if object == 'tasklog' and action == 'delete':
            self.delete_task(args)
        if object == 'pomlog' and action == 'show':
            self.pomlog_show(args)
        if object == 'task' and action == 'show':
            self.show_task(args)
        if object == 'task' and action == 'edit':
            self.edit_task(args)
        if object == 'task' and action == 'add':
            self.add_pomodorro(args)
        if object == 'task' and action == 'delete':
            self.delete_pomodorro(args)
        if object == 'pomodorro' and action == 'show':
            self.show_pomodorro(args)
        if object == 'pomodorro' and action == 'goal':
            self.pomodorro_goal(args)
        if object == 'pomodorro' and action == 'tag':
            self.pomodorro_tag(args)
        if object == 'pomodorro' and action == 'edit':
            self.pomodorro_edit(args)
        if object == 'timer' and action == 'set':
            self.timer_set_active(args)

    def settings_show(self, args):
        """ Display the user settings variables."""
        options = args["options"]
        self.settings.show(options)

    def settings_set(self, args):
        """ Modify the user settings variables."""
        options = args["options"]
        self.settings.set(options)

    def tasklog_show(self, args):
        """ Display the tasks."""
        options = args["options"]
        self.task_log.show(options)

    def add_task(self, args):
        """ Create a task."""
        options = args["options"]
        self.task_log.add(options)

    def delete_task(self, args):
        """ Delete a task."""
        options = args["options"]
        self.task_log.delete(options)

    def show_task(self, args):
        """ Display a task's information."""
        task_id = args["object_id"]
        options = args["options"]
        self.task_log.show_task(task_id, options)

    def edit_task(self, args):
        """ Modify a task's information."""
        task_id = args["object_id"]
        options = args["options"]
        changed_repeats_type, new_repeats = self.task_log.edit_task(task_id, options)
        if changed_repeats_type:
            self.recurrence_manager.update_edited_task(task_id, new_repeats)

    def pomlog_show(self, args):
        """ Display the pomodorros."""
        options = args["options"]
        self.pomodorro_log.show(options)

    def show_pomodorro(self, args):
        """ Display a pomodorro's information."""
        pom_id = args["object_id"]
        options = args["options"]
        self.pomodorro_log.show_pomodorro(pom_id, options)

    def add_pomodorro(self, args):
        """ Create a pomodorro."""
        task_id = args["object_id"]
        options = args["options"]
        self.pomodorro_log.add(task_id, options)

    def delete_pomodorro(self, args):
        """ Delete a pomodorro."""
        task_id = args["object_id"]
        options = args["options"]
        self.pomodorro_log.delete(task_id, options)

    def pomodorro_tag(self, args):
        """ Modify the pomodorro's tag."""
        pom_id = args["object_id"]
        options = args["options"]
        self.pomodorro_log.set_tag(pom_id, options)

    def pomodorro_goal(self, args):
        """ Modify the pomodorro's goal."""
        pom_id = args["object_id"]
        options = args["options"]
        self.pomodorro_log.set_goal(pom_id, options)

    def pomodorro_edit(self, args):
        """ Modify the selected pomodorro attribute."""
        pom_id = args["object_id"]
        options = args["options"]
        self.pomodorro_log.edit(pom_id, options)

    def timer_set_active(self, args):
        """ Set a pomodorro to active, and enter timer mode."""
        pom_id = args["object_id"]
        active_pomodorro = self.pomodorro_log.log[pom_id]
        t = Timer(self.model, self.task_log, self.pomodorro_log, active_pomodorro)
        t.launch_timer_menu()
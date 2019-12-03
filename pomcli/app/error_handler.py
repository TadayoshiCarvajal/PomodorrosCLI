class ErrorHandler:
    def __init__(self, settings, model, task_log, pomodorro_log):
        self.settings = settings
        self.task_log = task_log
        self.valid_task_ids = task_log.ids
        self.valid_task_names = task_log.names
        self.pomodorro_log = pomodorro_log
        self.valid_tags = pomodorro_log.tags
        self.valid_pom_ids = pomodorro_log.ids
        self.model = model

        # The values that can be modified by a user.
        self.valid_settings = {
            'pomodorro_length' : int,
            'rest_length' : int,
            'column_width' : int
        }

        # The valid objects command may involve.
        self.valid_objects = {   
                                "settings", 
                                "tasklog", 
                                "pomlog", 
                                "task", 
                                "pomodorro",
                                "timer",
                            }

        # The mapping from alternative name to official name of an object.
        self.alias = {
                                'pom' : "pomodorro",
                                'tasks' : "tasklog",
                                'poms' : "pomlog",
                                "settings" : "settings", 
                                "tasklog" : "tasklog", 
                                "pomlog" : "pomlog", 
                                "task" : "task", 
                                "pomodorro" : "pomodorro",
                                "timer" : "timer"
        }

        # The valid actions allowed for each command object.
        self.valid_actions = {
                                "settings" : {"set", "show"}, 
                                "tasklog" : {"show", "add", "delete"},
                                "pomlog" : {"show"},
                                "task" : {"show", "add", "delete", "edit"},
                                "pomodorro" : {"show", "tag", "goal"},
                                "timer" : {"set"}
                            }

        # The attributes of a task that a user may modify.
        self.editable_task_attributes = {"name" : str, 
                                        "repeats" : str}

        # A listing of the various error messages the ErrorHandler object might output.
        self.message = {
            "missing_object" : f"The object is missing. Object must be one of: {str(self.valid_objects)}.",
            "invalid_object" : f"The object is invalid. Object must be one of: {str(self.valid_objects)}.",
            "missing_action" : f"The action is missing.",
            "invalid_action" : f"The action is invalid.",
            "missing_pom_id" : f"The pomodorro ID is missing.",
            "invalid_pom_id" : f"There is no pomodorro with that pom_id or tag.",
            "missing_task_id" : f"The task ID is missing.",
            "invalid_task_id" : f"There is no task with that task_id or name.",
            "no_options" : f"This command takes options and none were specified.",
            "has_options" : f"This command doesn't take options.",
            "invalid_options_count" : f"The number of options is invalid.",
            "task_already" : f"A task with that name already exists.",
            "pom_already" : f"A pomodorro with that tag already exists.",
            "not_alnum" : f"Task names and pomodorro tags can only contain letters, digits, and spaces.",
            "first_not_alpha" : f"Task names and pomodorro tags must begin with a letter (a-z or A-Z).",
            "option_equal_invalid" : f"Options must be specified as attribute=value.",
            "invalid_repeats" : f"Value of repeats must be once, daily, weekly, monthly, or yearly.",
            "already_active" : f"There is already an active pomodorro.",
            "already_completed" : f"That pomodorro has already been completed.",
            "invalid_option" : f"An invalid option was detected."
            }

    # Helper functions for error checking
    def valid_input(self, args):
        """ Returns True if the input string is valid else False.
        
        Here, valid means that the object, object id, and action are all valid.
        Options are validated later in the handle_input_options_errors method."""

        return self.has_valid_structure(args) and not self.handle_input_options_errors(args)

    def has_valid_structure(self, args):
        """ Checks to see that the command has valid structure.

        For non-object-ID commands, <object> <action> <options> is required.
        Otherwise, <object> <object_id> <action> <options> is required. """
        # Check if object is valid.
        object = args["object"] if "object" in args else None
        if not object:
            print(self.message["missing_object"])
            return False

        if object not in self.alias:
            print(self.message["invalid_object"])
            return False

        if self.alias[object] not in self.valid_objects:
            print(self.message["invalid_object"])
            return False
        
        # Check if the action is valid.
        action = args["action"] if "action" in args else None
        if not action:
            print(self.message["missing_action"])
            return False

        if action not in self.valid_actions[self.alias[object]]:
            print(self.message["invalid_action"])
            return False

        # Check if Object ID is valid.
        if object == "timer" and action == "set":
            object_id = args["object_id"] if "object_id" in args else None
            if not object_id:
                print(self.message["missing_pom_id"])
                return False

        if self.alias[object] in {"pomodorro", "task"}:
            object_id = args["object_id"] if "object_id" in args else None

            if self.alias[object] == "pomodorro":
                if not object_id:
                    print(self.message["missing_pom_id"])
                    return False
                
                if not ((object_id.isdigit() and int(object_id) in self.valid_pom_ids) \
                    or object_id in self.valid_tags):
                    print(self.message["invalid_pom_id"])
                    return False

            if self.alias[object] == "task":
                if not object_id:
                    print(self.message["missing_task_id"])
                    return False
                
                if not ((object_id.isdigit() and int(object_id) in self.valid_task_ids) \
                    or object_id in self.valid_task_names):
                    print(self.message["invalid_task_id"])
                    return False
        return True

    def handle_input_options_errors(self, args):
        """ Handles invalid input options.

        Returns True if command options triggered an error, and prints the error message.
        Otherwise, returns False if the options are acceptable."""

        object = args["object"]
        action = args["action"]
        if "object_id" in args:
            object_id = args["object_id"]
        if "options" in args:
            options = args["options"]

        # Settings commands
        if object == 'settings' and action == 'show':
            return self.handle_settings_show_errors(options)
        if object == 'settings' and action == 'set':
            return self.handle_settings_set_errors(options)
        
        # Tasklog commands
        if object == 'tasklog' and action == 'show':
            return self.handle_task_log_show_errors(options)
        if object == 'tasklog' and action == 'add':
            return self.handle_task_add_errors(options)
        if object == 'tasklog' and action == 'delete':
            return self.handle_task_delete_errors(options)

        # Task commands
        if object == 'task' and action == 'show':
            return self.handle_show_task_errors(options)
        if object == 'task' and action == 'edit':
            return self.handle_edit_task_errors(options)
        if object == 'task' and action == 'add':
            return self.handle_pomodorro_add_errors(options)
        if object == 'task' and action == 'delete':
            return self.handle_pomodorro_delete_errors(options)

        # PomodorroLog commands
        if object == 'pomlog' and action == 'show':
            return self.handle_pom_log_show_errors(options)

        # Pomodorro commands
        if object == 'pomodorro' and action == 'show':
            return self.handle_show_pomodorro_errors(options)
        if object == 'pomodorro' and action == 'tag':
            return self.handle_set_tag_errors(options)
        if object == 'pomodorro' and action == 'goal':
            return self.handle_set_goal_errors(options)

        # Timer commands
        if object == 'timer' and action == 'set':
            return self.handle_timer_set_errors(object_id, options)

    def has_options(self, options):
        """ Checks if there are any options."""

        if options:
            print(self.message["has_options"])
            return True
        return False

    def has_no_options(self, options):
        """ Checks if there are not any options."""

        if not options:
            print(self.message["no_options"])
            return True
        return False
    
    def has_invalid_size(self, iterable, required_length=None, min_length=None, max_length=None):
        """ Checks that an iterable (usually options), meets a required size.
        
        Required size can be an explicit integer value, or specified as a 
        range using min_length and max_length parameters."""

        size = len(iterable)
        if min_length:
            if size < min_length:
                print(self.message["invalid_options_count"])
                return True
        if max_length:
            if size > max_length:
                print(self.message["invalid_options_count"])
                return True
        if required_length:
            if size != required_length:
                print(self.message["invalid_options_count"])
                return True
        
        return False

    def is_existing_task(self, task_id):
        """ Checks to see that a task exists."""

        if task_id in self.task_log.log:
            print(self.message["task_already"])
            return True
        return False

    def is_existing_pomodorro(self, pom_id):
        """Checks to see that a pomodorro exists."""

        if pom_id in self.pomodorro_log.log:
            print(self.message["pom_already"])
            return True
        return False

    def is_invalid_identifier(self, identifier):
        """ Checks to see that a given task name or pomodorro tag is valid.
        
        A valid identifier, must be alpha-numeric with the first character alpha."""

        if not identifier.replace(" ", "").isalnum():
            print(self.message["not_alnum"])
            return True
        if not identifier[0].isalpha():
            print(self.message["first_not_alpha"])
            return True
        
        return False

    def task_doesnt_exist(self, task_id):
        """ Checks to see a task does not exist."""

        if task_id.isdigit():
            task_id = int(task_id)
        if task_id not in self.task_log.log:
            print(self.message["invalid_task_id"])
            return True
        return False

    def pom_doesnt_exist(self, pom_id):
        """ Checks to see that a pomodorro does not already exist."""

        if pom_id not in self.pomodorro_log.log:
            print(self.message["invalid_pom_id"])
            return True
        return False

    def invalid_option_with_equal(self, option):
        """ Checks assignment options are valid.
        
        Assignment options, options in the form <attribute>=<value> are valid
        iff they have length 2 when split using the = as the delimiter."""

        if len(option.split("=")) != 2:
            print(self.message["option_equal_invalid"])
            return True
        return False

    def invalid_repeats_value(self, repeats):
        """ Checks to see a valid value of repeats was assigned.
        
        Tasks and pomodorros may repeat once, daily, weekly, monthly, or yearly."""

        if repeats.lower() not in {"once", "daily", "weekly", "monthly", "yearly"}:
            print(self.message["invalid_repeats"])
            return True
        return False

    def identifier_to_num(self, identifier):
        """ Converts a string ID to integer form.
        
        If an identifier is given in integer form, it is converted to an integer.
        Since object_ids are given via the command-line, task_id and pomodorro_id
        will be in the form of a string, i.e. '123', as opposed to 123. This 
        method will check to see that such values are ID's and then converts
        them if they are."""

        if identifier.isdigit():
            return int(identifier)
        else:
            return identifier

    def already_active_pomodorro(self):
        """ Checks to see if a pomodorro is already set to active."""

        if self.model.get_active_pomodorro():
            print(self.message["already_active"])
            return True
        return False

    def already_completed_pomodorro(self, pom_id):
        """ Checks to see if a pomodorro has already been completed."""

        pom_id = self.tag_to_id_num(pom_id)
        if self.model.is_complete(pom_id):
            print(self.message["already_completed"])
            return True
        return False

    def tag_to_id_num(self, name):
        """ Given a pomodorro tag, returns the corresponding pomodorro's ID."""

        return self.pomodorro_log.log[name].pom_id

    # Settings command related Errors
    def handle_settings_show_errors(self, options):
        """ Handle the specific errors involved in the settings show command.
        
        A user may specify settings variable as arguments to show only those
        specific commands. This method checks to ensure thatthose variables 
        are valid."""

        for option in options:
            if option not in self.valid_settings:
                print(f"{option} is not a valid setting.")
                return True
        return False

    def handle_settings_set_errors(self, options):
        """ This method is called when an option is invalid.

        There are 4 reasons an option might be invalid: there was no options,
        an option is missing the equal sign, an option specifies an attribute
        which is not a valid attribute of the Settings class, or the option
        specifies a type which is invalid fort the specified attribute. """

        if self.has_no_options: return True

        for option in options:
            option_components = option.split("=")
            if len(option_components) != 2:
                print(f"Options must be in the form: <attribute>=<value>.")
                return True

            attr = option_components[0]
            val = option_components[1]

            if attr not in self.valid_settings:
                print(f"{attr} is not a valid attribute.")
                return True

            try:
                val = self.valid_settings[attr](val)
            except ValueError:
                print(f"{val} is an invalid value for {attr}.")
                return True
            
        return False

    # TaskLog command related Errors
    def handle_task_log_show_errors(self, options):
        """ Parses the options to make sure they are valid.
        
        This method parses the options, validates them, and also checks that
        they do not conflict."""
        valid_options = {"repeating", "once"}

        if self.has_invalid_size(options, min_length = 0, max_length = 1): return True

        if options and options[0] not in valid_options: 
            print(self.message["invalid_option"])
            return True

        return False

    def handle_task_add_errors(self, options):
        """ Handles the potential errors when adding tasks.
        
        The command tasklog add 'name' 'repeats', can take between 2 options:
        The task name and the repeats value. An error can occur if the user
        uses a task name which already exists which is not allowed since task
        names must be unique, or an invalid number of arguments are specified."""

        if self.has_no_options(options): return True

        if self.has_invalid_size(options, max_length=2): return True

        if self.is_existing_task(options[0]): return True
        
        if self.is_invalid_identifier(options[0]): return True

        if len(options) == 2:
            if self.invalid_repeats_value(options[1]): return True

        return False

    def handle_task_delete_errors(self, options):
        """ Handles the potential error that occur when deleting.
        
        The deletion command is tasklog delete task_id, where task_id can
        be the actual task_id or the name of the task. The errors that might
        occur are the user does not specify a task_id or too options are specified,
        and the other error is the id that is passed is not a valid task_id or name."""

        if self.has_invalid_size(options, required_length=1): return True

        if self.task_doesnt_exist(options[0]): return True

        return False

    # Task command related Errors
    def handle_show_task_errors(self, options):
        """ Handles the potential error that occur when showing task.
        
        The command task task_id displays a more detailed view of the task
        that is specified by the task_id. This method checks if the task_id
        is valid first."""

        valid_options = {"brief"}

        if self.has_invalid_size(options, min_length = 0, max_length = 1): return True

        if options and options[0] not in valid_options: 
            print(self.message["invalid_option"])
            return True

        return False

    def handle_edit_task_errors(self, options):
        """ Handles the potential error that occur when deleting.
        
        The deletion command is tasklog delete task_id, where task_id can
        be the actual task_id or the name of the task. The errors that might
        occur are the user does not specify a task_id or too options are specified,
        and the other error is the id that is passed is not a valid task_id or name."""

        if self.has_invalid_size(options, min_length=1, max_length=2): return True

        for option in options:
            if self.invalid_option_with_equal(option): return True

            attribute, value = option.split("=")
            if attribute not in self.editable_task_attributes:
                print(f"{attribute} is not an editable task attribute.")
                return True

            if attribute == 'name':
                if self.is_existing_task(value): return True
                if self.is_invalid_identifier(value): return True

            if attribute == 'repeats':
                if self.invalid_repeats_value(value): return True

        return False

    def handle_pomodorro_add_errors(self, options):
        """ Handles the potential errors when adding pomodorros.
        
        The command task add 'tag' 'goal', can take between 1 and 2 options:
        The tag and the goal values. An error can occur if the user
        uses a tag name which already exists which is not allowed since tags
        must be unique, or an invalid number of arguments are specified,
        or the options are not in the form argument=value, or the arguments
        and values in the option are not valid, or the task_id is not valid."""

        if self.has_invalid_size(options, max_length=2): return True

        for option in options:
            if self.invalid_option_with_equal(option): return True

        specified_options = {option.split("=")[0] : option.split("=")[1] for option in options }
        tag = specified_options["tag"] if "tag" in specified_options else None
        goal = specified_options["goal"] if "goal" in specified_options else None

        if tag and self.is_existing_pomodorro(tag): return True
        if tag and self.is_invalid_identifier(tag): return True

        return False

    def handle_pomodorro_delete_errors(self, options):
        """ Handles the potential errors that occur when deleting.
        
        The deletion command is task task_id delete pom_id, where task_id can
        be the actual task_id or the name of the task and pom_id can be the 
        actual pom_id or the tag if there is one. The errors that might
        occur are the user does not specify a task_id or too options are specified,
        and the other error is the id that is passed is not a valid task_id or name."""
        
        if self.has_invalid_size(options, required_length=1): return True

        if self.pom_doesnt_exist(self.identifier_to_num(options[0])): return True

        return False

    # PomodorroLog related Errors
    def handle_pom_log_show_errors(self, options):
        """ Parses the options to make sure they are valid.
        
        This method parses the options, validates them, and also checks that
        they do not conflict."""
        valid_options = {"history"}

        if self.has_invalid_size(options, min_length = 0, max_length = 1): return True

        if options and options[0] not in valid_options: 
            print(self.message["invalid_option"])
            return True

        return False

    # Pomodorro related Errors
    def handle_show_pomodorro_errors(self, options):
        """ Handles the potential error that occur when showing a pomodorro.
        
        The command pom pom_id displays a more detailed view of the pomodorro. 
        This method checks if the pom_id is valid first."""

        valid_options = {"brief"}

        if self.has_invalid_size(options, min_length = 0, max_length = 1): return True

        if options and options[0] not in valid_options: 
            print(self.message["invalid_option"])
            return True

        return False

    def handle_set_tag_errors(self, options):
        """ Handles the potential error that occur when setting the goal
        for a pomodorro.
        
        The errors are that the current pom_id for the pomodorro is an
        invalid pomodorro id, or the new tag is already in use, or the new
        tag is not a valid tag name (i.e. must be alphanumeric with alpha first
        letter), or too many options were specified. 
        Returns False if none of the errors were handled. """

        if self.is_existing_pomodorro(" ".join(options)): return True

        if self.is_invalid_identifier(" ".join(options)): return True

        return False

    def handle_set_goal_errors(self, options):
        """ Handles the potential errors that occur when setting the goal
        for a pomodorro."""

        if self.has_no_options(options): return True

        return False

    # Timer related Errors
    def handle_timer_set_errors(self, pom_id, options):
        """ Handles the possible errors that can occur when using the command timer set.

        The command `timer set <object_id>` requires that object_id is a valid object_id.
        It is valid if it is an existing pomodorro and not completed. 
        Furthermore, only one pomodorro may be active at a time. """
        if self.pom_doesnt_exist(pom_id): return True

        if self.already_active_pomodorro(): return True

        if self.already_completed_pomodorro(pom_id): return True
        return False
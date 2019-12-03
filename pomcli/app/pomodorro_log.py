class PomodorroLog:
    """ A collection of pomodorros with high-level functionality to manage those pomodorros.

    When modifications, additions, or deletions of pomodorros take place, they must go through
    the PomodorroLog, which serves as a collection of all pomodorros belonging to the user, and
    acts as the manager of those pomodorros."""
    def __init__(self, pomodorros, model, settings, task_log):
        self.log = {}
        self.tags = set()
        self.ids = set()
        self.task_log = task_log
        self.settings = settings
        self.model = model
        self.generate_pomodorros(pomodorros)
        self.valid_attributes = {'tag', 'goal'}
    
    def get_pomodorro(self, pom):
        """ Uses pomodorro information from the database to create a pomodorro object."""

        from .pomodorro import Pomodorro

        pom_id = pom[0]
        tag = pom[1]
        task_id = self.task_log.log[pom[2]].name
        length = pom[3]
        rest = pom[4]
        goal = pom[5]
        active = pom[6]
        completed = pom[7]
        start_time = pom[8]
        end_time = pom[9]
        time_spent = pom[10]
        historic_tag = pom[11]

        return Pomodorro(pom_id, tag, task_id, length, rest, goal, 
                        active, completed, start_time, end_time, 
                        time_spent, historic_tag)

    def generate_pomodorros(self, pomodorros):
        """ Adds the pomodorros to the log dictionary. 
        
        Iterates through the list of pomodorros and adds them to the log,
        the tags, and id attributes, the first of which is a dictionary
        with keys as pom_id or tag if the tag is not None, and the tags 
        and id are sets. """
    
        for pom in pomodorros:
            pomodorro = self.get_pomodorro(pom)
            pom_id = pomodorro.pom_id
            tag = pomodorro.tag
            self.log[pom_id] = pomodorro
            self.ids.add(pom_id)
            if tag:
                self.log[tag] = pomodorro
                self.tags.add(tag)

    def show(self, options):
        """ Displays the tasks inside of the PomodorroLog.
        
        Prints the title, Pomodorro Log:, on its own line and then on each subsequent
        line, prints the tasks if there are any."""

        print("Pomodorro Log:")
        cw = self.settings.column_width
        header = f"{'Task':^{cw}s}|{'PomID':^{cw}s}|{'Tag':^{cw}s}|{'Goal':^{cw}s}"
        print(header)
        print("-"*(4*cw+3))

        history_mode = False
        if options and options[0] == 'history':
            history_mode = True

        for pom_id in self.ids:
            pomodorro = self.log[pom_id]

            if not history_mode and not pomodorro.completed:
                print(pomodorro.__str__(self.settings))
            elif history_mode and pomodorro.completed:
                print(pomodorro.__str__(self.settings, history=True))

    def add(self, task_id, options):
        """ Adds a Pomodorro to the specified Task.
        
        When pomodorros are added, they can also be created with a goal
        and a tag. A Goal is a string that describes what the user wishes
        to accomplish with this pomodorro. The tag is a nickname for the 
        Pomodorro to make referring to it more intuitive (as opposed to 
        using pom_id)."""

        # convert from minutes to seconds:
        length, rest = self.settings.pomodorro_length*60, self.settings.rest_length*60 
        if task_id in self.task_log.names:
            task_id = int(self.task_log.log[task_id].task_id)
        if not options: # add a pomodorro without tag or goal data.
            self.model.add_pomodorro(task_id, "", length, rest, "")
        else:
            specified_options = {option.split("=")[0] : option.split("=")[1] for option in options }
            tag = specified_options["tag"] if "tag" in specified_options else ""
            goal = specified_options["goal"] if "goal" in specified_options else ""
            self.model.add_pomodorro(task_id, tag, length, rest, goal)

    def delete(self, task_id, options):
        """ Deletes the specified pomodorro.
        
        A pomodorro must be specified by either pom_id or tag. """

        if task_id in self.task_log.names:
            task_id = self.task_log.log[task_id].task_id
        task_id = int(task_id)
        
        pom_id = options[0]
        if pom_id in self.tags:
            pom_id = self.log[pom_id].pom_id
        pom_id = int(pom_id)

        self.model.delete_pomodorro(task_id, pom_id)
    
    def show_pomodorro(self, pom_id, options):
        """ Displays the specified pomodorros's information.
        
        A pomodorro must be specified by either pom_id or tag."""
        option = None
        if options:
            option = options[0]

        if pom_id in self.tags:
            pom_id = int(self.log[pom_id].pom_id)

        pom = self.log[int(pom_id)]
        if option == "brief":
            pom.show(brief=True)
        else:
            pom.show()

    def set_tag(self, pom_id, options):
        """ Changes the specified pomodorros's tag to the specified tag.
        
        A valid tag must not be a tag that is already in use. """
        if pom_id in self.tags:
            pom_id = int(self.log[pom_id].pom_id)

        new_tag = " ".join(options)
        self.model.change_tag(pom_id, new_tag)

    def set_goal(self, pom_id, options):
        """ Changes the specified pomodorros's goal to the specified goal.
        
        A valid tag must not be a tag that is already in use. """

        if pom_id in self.tags:
            pom_id = int(self.log[pom_id].pom_id)

        new_goal = " ".join(options)
        self.model.change_goal(pom_id, new_goal)

    def __getitem__(self, name):
        return self.log[name]

    def __setitem__(self, name, value):
        self.log[name] = value

    def __len__(self):
        return len(self.log)
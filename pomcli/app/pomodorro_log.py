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
        priority = self.task_log.log[pom[2]].priority
        length = pom[3]
        rest = pom[4]
        goal = pom[5]
        active = pom[6]
        completed = pom[7]
        start_time = pom[8]
        end_time = pom[9]
        time_spent = pom[10]
        historic_tag = pom[11]
        expired = pom[12]
        due = pom[13]
        
        return Pomodorro(pom_id, tag, task_id, priority, length, rest, goal, 
                        active, completed, start_time, end_time, 
                        time_spent, historic_tag, expired, due)

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
        header = f"{'Task':^{cw}s}|{'PomID':^{cw}s}|{'Tag':^{cw}s}|{'Priority':^{cw}s}|{'Length':^{cw}s}|{'Rest':^{cw}s}|{'Goal':^{cw}s}"
        print(header)
        N = header.count('|') + 1
        print("-"*(N*cw+(N-1)))

        history_mode = False
        if options and options[0] == 'history':
            history_mode = True

        pomodorros = sorted([self.log[pom_id] for pom_id in self.ids], key=lambda x: x.priority, reverse=True)
        for pomodorro in pomodorros:

            if not history_mode and not pomodorro.completed and not pomodorro.expired:
                print(pomodorro.__str__(self.settings))
            elif history_mode and pomodorro.completed:
                print(pomodorro.__str__(self.settings, history=True))
            
    def add(self, task_id, options):
        """ Adds a Pomodorro to the specified Task.
        
        When pomodorros are added, they can also be created with a goal, a tag,
        a pomodorro length, and a rest length. A Goal is a string that describes 
        what the user wishes to accomplish with this pomodorro. The tag is a nickname 
        for the Pomodorro to make referring to it more intuitive (as opposed to 
        using the pom_id)."""

        if task_id in self.task_log.names:
            task_id = int(self.task_log.log[task_id].task_id)
        task_repeats = self.task_log.log[task_id].repeats
        # convert from minutes to seconds
        length, rest = self.task_log.log[task_id].pomodorro_length*60, self.task_log.log[task_id].rest_length*60 
        specified_options = {option.split("=")[0] : option.split("=")[1] for option in options }
        tag = specified_options["tag"] if "tag" in specified_options else ""
        goal = specified_options["goal"] if "goal" in specified_options else ""
        length = int(specified_options["pomodorro_length"])*60 if "pomodorro_length" in specified_options else length
        rest = int(specified_options["rest_length"])*60 if "rest_length" in specified_options else rest
        once_due = specified_options['due'] if 'due' in specified_options else None
        due = self.get_due(task_repeats, once_due)

        self.model.add_pomodorro(task_id, tag, length, rest, goal, due)

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

    def edit(self, pom_id, options):
        """ Changes the specified pomodorros's goal to the specified goal.
        
        A valid tag must not be a tag that is already in use. """

        if pom_id in self.tags:
            pom_id = int(self.log[pom_id].pom_id)

        task_id = self.task_log.log[self.log[pom_id].task].task_id
        if task_id in self.task_log.names:
            task_id = int(self.task_log.log[task_id].task_id)
        task_repeats = self.task_log.log[task_id].repeats

        # Get current pomodorro data
        tag = self.log[pom_id].tag
        goal = self.log[pom_id].goal
        length = self.log[pom_id].length
        rest = self.log[pom_id].rest
        due = self.log[pom_id].due

        # Get new pomodorro data
        specified_options = {option.split("=")[0]:option.split("=")[1] for option in options}
        tag = specified_options['tag'] if 'tag' in specified_options else tag
        goal = specified_options['goal'] if 'goal' in specified_options else goal
        length = int(specified_options['pomodorro_length'])*60 if 'pomodorro_length' in specified_options else length
        rest = int(specified_options['rest_length'])*60 if 'rest_length' in specified_options else rest
        once_due = specified_options['due'] if 'due' in specified_options else None
        if once_due:
            due = self.get_due(task_repeats, once_due)

        self.model.edit_pomodorro(pom_id, tag, goal, length, rest, due)

    def get_due(self, repeats, once_due):
        """ Returns the due date of the pomodorro.
        
        Uses the repeats and repeats_frequency values of the task to 
        calculate the due date for the pomodorro."""
        import datetime
        import calendar

        # if once, due None
        if repeats == 'once':
            try:
                return datetime.datetime.strptime(once_due, '%Y-%m-%d %H:%M:%S.%f')
            except:
                try:
                    return datetime.datetime.strptime(once_due, '%Y-%m-%d %H:%M:%S')
                except:
                    try:
                        return datetime.datetime.strptime(once_due, '%Y-%m-%d %H:%M')
                    except:
                        return None

        # If daily, due midnight tonight.
        due = datetime.datetime.combine(datetime.datetime.today(), datetime.time(23, 59, 59, 999999))

        # If weekly, due midnight of this Sunday.
        if repeats == 'weekly':
            dow = datetime.datetime.today().weekday()
            td = 6 - dow # 0 if sunday, 6 if monday
            due += datetime.timedelta(days=td)

        # If monthly, due midnight of last day of month.
        elif repeats == 'monthly':
            year, month, day = due.year, due.month, due.day
            month_range = calendar.monthrange(year, month)
            last_day = month_range[-1]
            td = last_day - day
            due += datetime.timedelta(days=td)

        # If yearly, due midnight of last day of the year.
        elif repeats == 'yearly':
            last_day = datetime.datetime(due.year, 12, 31)
            td = (last_day - due).days + 1
            due += datetime.timedelta(days=td)
        return due 

    def __getitem__(self, name):
        return self.log[name]

    def __setitem__(self, name, value):
        self.log[name] = value

    def __len__(self):
        return len(self.log)
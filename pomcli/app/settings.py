class Settings:
    def __init__(self, args, model):
        self.model = model
        self.pomodorro_length = args["pomodorro_length"] # in minutes
        self.rest_length = args["rest_length"] # in minutes
        self.column_width = args["column_width"]

        self.valid_setting = {
            'pomodorro_length' : int,
            'rest_length' : int
        }

    def show(self, options):
        """ This method is called to display the settings data.

        When it's called with no options (empty list), all of the 
        settings data is displayed. Otherwise, the user may specify 
        precisely which settings attributes are to be printed.
        """
        if not options:
            s = self
        else:
            s = "Settings:\n"
            for option in options:
                s += f"\r\t" + f"{option} = {getattr(self, option)}\n"
        
        print(s)
        return s

    def set(self, options):
        """ This method is called when the user wants to set a settings attribute.

        We first check to make sure the options are valid. They can be invalid
        due to there not being any options, an option is missing an equal sign,
        the attribute is not a valid attribute, or the value is of invalid type.
        If an option is valid, we update the database using the model. """

        for option in options:
            attr, val = option.split("=")
            val = self.valid_setting[attr](val)
            self.model.settings_set(attr, val)
            print(f"{attr} successfully updated.")
        
    def __repr__(self):
        """A representation of the settings.

        This is what is displayed when the user uses the command "settings show".
        """
        s = f"""Settings:
        \r\tpomodorro_length = {self.pomodorro_length}
        \r\trest_length = {self.rest_length}"""
        return s
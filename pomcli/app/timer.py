class Timer:
    def __init__(self, model, task_log, pomodorro_log, pomodorro):
        self.model = model
        self.task_log = task_log
        self.pomodorro_log = pomodorro_log
        self.active_pomodorro = pomodorro
        self.active_task = self.task_log.log[self.active_pomodorro.task]
        self.length = self.active_pomodorro.length
        self.rest_length = self.active_pomodorro.rest


        # The menu available depending on the state.
        self.menus = {
            "Start" : ["Start", "Done", "Exit"],
            "Pause" : ["Resume", "Done", "Exit"],
            "Resume" : ["Pause", "Done", "Exit"],
            "Rest" : ["Exit"]
        }
        self.state = "Start"
        self.menu = self.menus["Start"]

        # The state that we transition to when we select the first menu item.
        self.transition_state = {
            "Start" : "Resume",
            "Pause" : "Resume",
            "Resume" : "Pause"
        }

        # Timer information:
        self.start_time = 0
        self.pause_time = 0
        self.resume_time = 0
        self.elapsed_time = 0
        self.finish_time = 0
        self.pauses = 0
        
        # Set the specified pomodorro to active.
        self.model.set_active_pomodorro(self.active_pomodorro)
        self.active_pomodorro = self.get_active_pomodorro()

        # The number of incomplete pomodorros belonging to the same task.
        self.pomodorros_of_same_task = len(set([self.pomodorro_log.log[pomodorro].pom_id \
            for pomodorro in self.pomodorro_log.log \
            if self.pomodorro_log.log[pomodorro].task == self.active_pomodorro.task \
            and not self.pomodorro_log.log[pomodorro].completed]))

    def switch_state(self):
        """ Transition us to the next state.
        
        This method is invoked if we are in Start state and the user selects Start,
        if we are in the Pause state and user selects Resume,
        or if we are in Resume and the user selects Pause.
        
        We transition as follows:
            Start -> Resume
            Resume -> Pause
            Pause -> Resume"""

        self.state = self.transition_state[self.state]
        self.menu = self.menus[self.state]

    def begin(self):
        """ This begins the timer.
        
        We start a timer using the time module from the standard library.
        We mark the pomodorro as active in the database, and switch our 
        state from Start to Resume."""
        from time import time

        self.start_time = time()
        self.resume_time = time()
        self.model.begin_pomodorro(self.active_pomodorro, self.start_time)
        self.switch_state()
        self.active_pomodorro = self.get_active_pomodorro()
        
    def pause(self):
        """ This pauses the timer.
        
        We store the time that has elapsed into the elapsed_time variable
        and we use this variable to help us keep track of how much time has
        passed, and increment the number of pauses. We switch our state."""
        from time import time

        self.pause_time = time()
        self.elapsed_time += int(self.pause_time - self.resume_time)
        self.pauses += 1
        self.switch_state()

    def resume(self):
        """ This resume the timer.
        
        We update our resume_time variable and switch our state."""
        from time import time

        self.resume_time = time()
        self.switch_state()

    def cancel(self):
        """ This cancels the timer.
        
        If the pomodorro is in its rest phase, we can simply exit the 
        timer interface. Otherwise, we must first reset the pomodorro's 
        information to its default."""

        if self.state != "Rest":
            self.model.reset_pomodorro(self.active_pomodorro)

    def complete(self):
        """ Completes the pomodorro in its work phase.
        
        If the user wants to complete a pomodorro without having the timer
        run for the work time duration, they select the Done option which
        calls this method."""
        from time import time

        self.finish_time = time()
        self.start_time = self.finish_time if self.start_time == 0 else self.start_time
        self.resume_time = self.finish_time if self.resume_time == 0 else self.resume_time
        self.elapsed_time += int(self.finish_time - self.resume_time)
        self.model.complete_pomodorro(  self.active_pomodorro, self.start_time, 
                                        self.finish_time, self.elapsed_time)

        if self.active_task.repeats == 'once' \
            and self.active_task.pomodorro_complete \
            and self.pomodorros_of_same_task == 1: # this is last pomodorro
            self.model.complete_task(self.active_task.task_id)
        self.begin_rest()

    def begin_rest(self):
        """ This begins the rest phase of the pomodorro.

        The timer data is set to its defaults so we can start a new countdown
        for the rest phase."""
        from time import time

        self.active_pomodorro = "Rest"
        self.state = "Rest"
        self.menu = self.menus["Rest"]
        self.start_time = 0
        self.pause_time = 0
        self.resume_time = time()
        self.elapsed_time = 0
        self.finish_time = 0
        self.pauses = 0

    def get_active_pomodorro(self):
        """ Retrieves the pomodorro with its active variable set to True."""

        pom_info = self.model.get_active_pomodorro()
        if pom_info:
            return self.pomodorro_log.get_pomodorro(pom_info)
        else:
            return None

    def get_time_remaining(self, total_time, time_passed):
        """ Helper function used for determining the remaining time.
        
        Given total time and the time that has passed, returns the difference."""
        return total_time - time_passed

    def launch_timer_menu(self):
        """ The timer UI."""
        import curses

        def print_menu(stdscr, selected_row_idx, time_elapsed):
            stdscr.clear()
            h, w = stdscr.getmaxyx()

            current_pomodorro = self.active_pomodorro.__repr__()
            temp = current_pomodorro.splitlines()
            info = []
            for i in range(0, len(temp), 2):
                temp[i] = temp[i].strip()
                temp[i] = temp[i].replace("\n", "")
                info.append(temp[i])
            
            # Display Pomodorro information
            for idx, row in enumerate(info):
                x = w//4 - len(info[0])//2
                y = h//2 - len(info)//2 + idx
                stdscr.addstr(y, x, info[idx])

            # Print Time Elapsed:
            time_string = self.seconds_to_time_string(time_elapsed)
            x = w//2 - len(time_string)//2
            y = 1
            stdscr.addstr(y, x, time_string)

            # Print Menu
            for idx, row in enumerate(self.menu):
                x = 3*w//4 - len(row)//2
                y = h//2 - len(self.menu)//2 + idx
                if idx == selected_row_idx:
                    stdscr.attron(curses.color_pair(1))
                    stdscr.addstr(y, x, row)
                    stdscr.attroff(curses.color_pair(1))
                else:
                    stdscr.addstr(y, x, row)

        def timer_menu(stdscr):
            from time import time, sleep

            curses.curs_set(0)
            stdscr.nodelay(True)
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
            current_row_idx = 0
            time_remaining = self.length
            print_menu(stdscr, current_row_idx, time_remaining)

            while 1:
                if self.state == "Resume":
                    time_elapsed = int(time() - self.resume_time) + self.elapsed_time
                    time_remaining = self.get_time_remaining(self.length, time_elapsed)
                elif self.state == 'Rest':
                    time_elapsed = int(time() - self.resume_time)
                    time_remaining = self.get_time_remaining(self.rest_length, time_elapsed)

                if self.state == "Resume" and time_remaining <= 0:
                    self.complete()
                    current_row_idx = 0
                elif self.state == "Rest" and time_remaining <= 0:
                    self.cancel()
                    break

                key = stdscr.getch()
                stdscr.clear()

                if key == curses.KEY_UP and current_row_idx > 0:
                    current_row_idx -= 1
                elif key == curses.KEY_DOWN and current_row_idx < len(self.menu) - 1:
                    current_row_idx += 1
                elif key == curses.KEY_ENTER or key in [10, 13] and self.menu[current_row_idx] == "Exit":
                    self.cancel()
                    break
                elif key == curses.KEY_ENTER or key in [10, 13] and self.menu[current_row_idx] == "Done":
                    self.complete()
                    current_row_idx = 0
                elif key == curses.KEY_ENTER or key in [10, 13] and self.menu[current_row_idx] == "Start":
                    self.begin()
                elif key == curses.KEY_ENTER or key in [10, 13] and self.menu[current_row_idx] == "Pause":
                    self.pause()
                elif key == curses.KEY_ENTER or key in [10, 13] and self.menu[current_row_idx] == "Resume":
                    self.resume()
                sleep(0.05) # give the cpu a rest

                print_menu(stdscr, current_row_idx, time_remaining)
                stdscr.refresh()

        curses.wrapper(timer_menu)

    def seconds_to_time_string(self, seconds):
        """ Given time in seconds, returns it in H:M:S format."""

        if seconds == 0:
            return "00:00:00"

        hours = seconds // 3600
        remaining_seconds = seconds - (hours * 3600)

        minutes = remaining_seconds // 60
        remaining_seconds = remaining_seconds - (minutes * 60)

        seconds = remaining_seconds

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
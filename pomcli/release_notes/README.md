# PomodorrosCLI 0.2.0 Release Notes
## January 28, 2020

## Features
* **Recurring Pomodorros** - Daily, Weekly, Monthly, and Yearly repeating Tasks will automatically expire and refresh Pomodorros based on the repeats value. Pomodorros now have due and expired variables to account for this change. Pomodorros that are not completed before the due date and time will be marked expired.
* **Once Due** - Pomodorros belonging to tasks that repeat once also have a due value and expired value, but the due can be specified to any date in the future by the user. It will also be marked expired when this date passes and the pomodorro has not been completed.
* **Task Pomodorro Length and Rest Lengths** - You can now specify a default pomodorro and rest length for each Task.
* **Priority** - You can now specify a priority for each Task which determines the ordering of the TaskLog and PomodorroLog.
* **More Settings** - Added settings: column_width and hide success. See the manual for more information.
* **Pomodorro-based Completion** - Added the ability to set nonrepeating (once) tasks to pomodorro_complete, which automatically completes the task once its final pomodorro is completed.
* **Unit Tests** - Added unit tests for testing the methods of the Model class. Many more unittests to be added in 0.3.0 ...

> `Note`: for additional information about these changes please consult the [user manual](../manual/README.md).

# PomodorrosCLI 0.1.0 Release Notes
## December 3, 2019

## Features
* **Settings** - The Settings object provides actions that allow the user to interact with their settings.
* **TaskLog** - The TaskLog object provides actions that allow the user to interact with the tasks they have created.
* **PomLog** - The PomLog object (short for pomodorrolog) provides actions that allow the user to interact with the pomodorros they have created.
* **Task** - The Task object allows the user to interact with a specified task that they have created.
* **Pomodorro** - The Pomodorro object allows the user to interact with a specified pomodorro that they have created.
* **Timer** - The Timer object allows the user to enter timer mode. Timer mode is where the user begins, works on, and completes pomodorros.

> `Note`: for more information about these objects, including how to use them, please see the [user manual](../manual/README.md).
import sys
import os
from app.interface import Interface
from app.model import Model
import sqlite3
"""
This is the driver program of the pomcli application.
This file will generate a new database if one does not exist,
and it will create the default user settings. All subsequent
commands made to this program will pass of the commands to
the interface.py file located in app/. From there,
all error handling and command execution is handled. 
"""

def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

if __name__ == "__main__":

    # Sets up the database if it hasn't been set up yet.
    #directory = sys.argv[1:][0]
    #os.chdir(directory)
    path = get_script_path() + '/app/'
    conn = sqlite3.connect(path+"pomodorros.db")
    model = Model(conn)
    try: 
        # First time using app
        model.initialize_tables()

    except sqlite3.OperationalError:
        # Subsequent uses of app
        settings = model.get_settings()
        task_log = model.get_task_log(settings)
        pomodorro_log = model.get_pomodorro_log(settings, task_log)
        ui = Interface(task_log, pomodorro_log, settings, model)
        ui.process_input(sys.argv[1:])
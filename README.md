# PomodorrosCLI

PomodorrosCLI (aka pomcli)  is an open source time management tool that lives in the command line. It enables the user to create Tasks and assign Pomodorros, or units of time, to those tasks, and uses an interactive timer mode which allows the user to begin, and work on those pomodorros, all  from the terminal.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

[Python3.7](www.python.org/downloads) or newer.


### Installing


Clone this repo to your environment. Hit the download button or from the terminal type:
```
git clone https://github.com/TadayoshiCarvajal/PomodorrosCLI
```


## Running the tests

There is a test_suite.py file located in the tests directory. It comes equipped with all of the unittests necessary for testing out the class methods within the application. In later versions, additional automated tests will be added as necessary. To run the tests, simply type into the terminal:
```
cd path_to_directory/PomodorrosCLI
python3 -m pomcli.tests.test_suite
```

## Deployment

Once you've downloaded or cloned a copy of PomodorrosCLI (see [Getting Started](#getting-started)), use a text editor or IDE to add the pomcli alias to your environment. On MacOS:
```
cd ~
open -a "Visual Studio Code" .bash_profile
```

Add the following line to create the alias to your pomcli/main.py file:
```
alias pomcli="python3 ~/Desktop/PomodorrosCLI/pomcli/main.py"
```
> `Note`: replace **~/Desktop/PomodorrosCLI/pomcli/main.py** with the location of your pomcli/main.py file
Once you've created the alias, save and close the .bash_profile file. Initialize the application with the following terminal command:
```
$ pomcli
```

If you see the message,
```
Successfully intialized PomodorrosCLI!
```
then congratulations! You are all set.

For help on getting started with PomodorrosCLI, please consult the [user manual](pomcli/manual/README.md).

## Built With

* [curses](https://docs.python.org/3/howto/curses.html) - The CLI tool used in timer mode
* [sqlite3](https://www.sqlite.org/index.html) - the database

## Authors

* **Tadayoshi Carvajal** - *Initial work* - [TadayoshiCarvajal](https://github.com/TadayoshiCarvajal)

## License

This project is licensed under the MIT License - see the [LICENSE.md](pomcli/resources/LICENSE.md) file for details

## Acknowledgments

* Hat tip to the creators and contributors of curses, python, the pomodorro technique, and anyone else who assisted in making this project a reality. 

## Coming Soon...

There is a lot more coming to `PomodorrosCLI` that is anticipated by version `1.0.0`. Some of these features include:

* `Recurrent Tasks and Pomodorros` - `0.3.0` - `repeats_frequency` to be added which will allow more customization for the user to define when repeating pomodorros are due/expire. Expected: TBD March 2020

* `More Options` - `0.4.0` - Many more options for the existing commands, including the ability to display how much time has been spent on a particular task, will be added. Expected: TBD April 2020

* `Recommender System` - `0.5.0` - Machine Learning system that uses historical usage data to predict what task/pomodorro should be worked on at any given time. Expected: TBD May 2020

* `Help object` - `0.6.0` - An additional command object which will take other command objects and actions as parameters, and display helpful information about them right from the terminal. Expected: TBD June 2020

* `Migrator Tool` - `0.7.0` - A tool that will allow users to migrate their pomodorros.db data from version to version. Expected: TBD July 2020
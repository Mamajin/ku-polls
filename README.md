## KU Polls: Online Survey Questions 

An application to conduct online polls and surveys based
on the [Django Tutorial project](https://docs.djangoproject.com/en/5.1/intro/tutorial01/), with
additional features.

This app was created as part of the [Individual Software Process](
https://cpske.github.io/ISP) course at [Kasetsart University](https://www.ku.ac.th).

## Installation

To be added. If the procedure is long, put it in the wiki or a separate file.

## Running the Application

To be added.

## Project Documents

All project documents are in the [Project Wiki](../../wiki/Home).

- [Vision Statement](../../wiki/Vision%20Statement)
- [Requirements](../../wiki/Requirements)
- [Project Plan](../../wiki/Project%20Plan)
- [Iteration 1](../../wiki/Iteration%201)
- [Iteration 2](../../wiki/Iteration%202)

## Installation

1. Open Terminal for macOS/Linux or Windows PowerShell/Command prompt for Windows

2. Clone this repository
    ```commandline
    git clone <repository link>
    ```

3. Change directory to ku-polls
    ```commandline
    cd ku-polls
    ```

4. Create a Python environment using this command line
    ```commandline
    python -m venv env
    ```

5. Activate virtual environment
   - For macOS/Linux
    ```commandline
    source env/bin/activate
    ```

    - For Windows
    ```commandline
    env\Scripts\activate
    ```

6. Install required packages
    ```commandline
    pip install -r requirements.txt
    ```

7. Initialize Database
    ```commandline
    python manage.py migrate
    ```

## Running the Application

1. Load poll data from a file
    ```commandline
    python manage.py loaddata data/<filename>
    ```

2. Run django server
    ```commandline
    python manage.py runserver
    ```


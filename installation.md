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
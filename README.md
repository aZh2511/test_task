# Test task for Junior Python Developer position

The task was to made an django app "alias" that will connect aliases with targets.
Aliases are available by alias value and target value. Methods of Alias Model:
1. Alias.get_aliases() - returns aliases following given conditions (Alias.get_aliases.__doc__ - for more info).
2. Alias.alias_replace() - replaces an existing alias with a new one (Alias.alias_replace.__doc__ - for more info).
3. Ordinary built-in django model.Model methods.

## Changes
1. Separate Alias method for getting data to be filtered.
2. Separate method for adding timezone for datetime type values IF needed! (if already provided - pass)
3. Filtering with Q optimized as recommended.


## How to install
1. Copy project to your computer.
2. Move to test_task folder (not test_task/test_task !).
3. Make sure python version is 3.8 at least
    ```commandline 
    python3 -V
    ```
    Otherwise run
    ```commandline
    sudo apt update
    sudo apt -y upgrade
    ```
4. Install pip:
    ```commandline
    sudo apt install -y python3-pip
    ```
5. Install required packages:
    ```commandline
    pip install requirements.txt
    ```
    or
    ```commandline
    pip3 install requirements.txt
    ```
6. Install python venv
    ```commandline
    sudo apt install -y python3-venv
    ```
7. Create python venv
    ```commandline
    python3 -m venv venv
    ```
8. Activate python venv
    ```commandline
    source venv/bin/activate
    ```
9. Move to test_task directory from current (must be test_task)
    ```commandline
    cd test_tesk/
    ```
10. Run
    ```commandline
    python3 manage.py makemigrations
    python3 manage.py migrate
    ```

### Run app
1. To run tests:
    ```commandline
    python3 manage.py test
    ```
2. To run django shell:
    ```commandline
    python3 manage.py shell
    ```
Now you can test Alias app functionality by your own. 
Don't forget to import everything!
```python
from alias.models import Alias
```
***

 
Best regards,
 
Andew Zheravin

andreyzheravin@gmail.com


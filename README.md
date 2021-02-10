# Test task for Junior Python Developer position

The task was to made an django app "alias" that will connect aliases with targets.
Aliases are available by alias value and target value. Methods of Alias Model:
1. Alias.get_aliases() - returns aliases following given conditions (Alias.get_aliases.__doc__ - for more info).
2. Alias.alias_replace() - replaces an existing alias with a new one (Alias.alias_replace.__doc__ - for more info).
3. Ordinary built-in django model.Model methods.

## Changes
1. Now error raising check in tests is made with self.assertRaises.
2. Optimized get_aliases. Only one hit db (used django.db.models.Q).
3. Added some type hints.
4. Overlapping check isn't made with iteration any more. Get all aliases with .filter(alias, target) and then look in that data with .filter() for any occurrences that can cause a Error.
5. Now Alias objects with the same alias value can refer to different targets unless they overlap.
6. Changed docstrings with the PEP-257 demands (Still not sure if it is exactly what PEP requires).


## How to install
1. Copy project to your computer.
2. Move to test_task folder (not test_task/test_task!).
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
Also you can use datetime without timezone, because I have made auto adding of timezone.


***

 
Best regards,
 
Andew Zheravin

andreyzheravin@gmail.com


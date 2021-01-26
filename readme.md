# monkey

### Overview

Monkey is a collection of scripts for making migratory changes between multiple databases.
MySQL Connectors have been setup for the Collaborations database and Posts database.

This project includes the following files and folders:

- requirements.txt - Dependencies exported via `pip freeze > requirements.txt`. Required for build/install.
- scripts - Initialization and setup scripts for testing locally.
- src
- - main.py - main program
- - common - common libraries (clients, connectors, etc.) for rewardStyle databases and services.
- - utils - Collection of utility functions for performing basic functions / conversions. 
- tests - Unit tests for the application code.

## Requirements

The configuration will be loaded from a local_dev.json file, however you can also set environment variables
through a launch configuration. Your VsCode launch.json should have a configuration like this:
```json
    {
      "name": "Python: Main",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/src/main.py",
      "console": "integratedTerminal",
      "env": {
        "PYTHONPATH":"./src",
        "COLLABS_DB_NAME":"collaborations",
        "COLLABS_SERVICE_MYSQL_HOST":"localhost",
        "COLLABS_SERVICE_MYSQL_PORT":"3306",
        "COLLABS_SERVICE_MYSQL_USER":"rspost",
        "COLLABS_SERVICE_MYSQL_PASSWORD":"dbpass",
        "POST_DB_NAME": "rspost",
        "POST_SERVICE_MYSQL_USER":"rspost",
        "POST_SERVICE_MYSQL_PASSWORD":"dbpass",
        "POST_SERVICE_MYSQL_HOST":"0.0.0.0",
        "POST_SERVICE_MYSQL_PORT":"3306",
        "ENVIRONMENT": "dev",
        "ENV": "dev",
      },
      "args": ["--config", "local_dev.json"]
    }
```
### Managing Dependencies

For installing dependencies, see the virtualenv [Installation Guide](https://docs.python-guide.org/dev/virtualenvs/) and [pipenv](https://pypi.org/project/pipenv/).
1. Generate a hashed `requirements.txt` out of our `Pipfile` dep file

```bash
# Create a hashed pip requirements.txt file only with our app dependencies (no dev deps)
pipenv lock -r > requirements.txt
pip install -r requirements.txt
```

Provided that you have requirements above installed, proceed by installing the application dependencies and development dependencies:

```bash
pipenv install
pipenv install -d
```
### Running locally

1. Setup the virtual environment: `python venv venv`
2. Source the virtual environment: `source ./venv/bin/activate`
3. Install the requirements: `pip install -r requirements.txt`
4. Execute the main.py: `python src/main.py --config local_dev.json`

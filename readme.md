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

### Prerequisites

To get started, see the following:

* [PyCharm](https://docs.aws.amazon.com/toolkit-for-jetbrains/latest/userguide/welcome.html)
* [IntelliJ](https://docs.aws.amazon.com/toolkit-for-jetbrains/latest/userguide/welcome.html)
* [VS Code](https://docs.aws.amazon.com/toolkit-for-vscode/latest/userguide/welcome.html)
* [Visual Studio](https://docs.aws.amazon.com/toolkit-for-visual-studio/latest/user-guide/welcome.html)
* [Visual Studio Code](https://aws.amazon.com/visualstudiocode/)

To use the AWS SAM CLI, you need the following tools:

* AWS CLI - [Install the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) and [configure it with the AWS credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html).
* AWS SAM CLI - [Install the AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html).
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community).

Requirements:

* [Python3.7](https://www.python.org/downloads/release/python-377/)
* [pipenv](https://pypi.org/project/pipenv/)

### Managing Dependencies

For installing dependencies, see the virtualenv [Installation Guide](https://docs.python-guide.org/dev/virtualenvs/) and [pipenv](https://pypi.org/project/pipenv/). For deployment, we use the Pipfile, however for SAM local development, we generate a requirements.txt.

1. Generate a hashed `requirements.txt` out of our `Pipfile` dep file
2. Install all dependencies directly to `build` sub-folder
3. Copy our function (post_event_handler.py) into `build` sub-folder

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

### Building with Docker

Build the image using the following command

```
$ docker build -t monkey:latest .
```
Run the Docker container using the command shown below.
```
$ docker run -d -p 5000:5000 monkey
```
The application will be accessible at http:127.0.0.1:5000 or if you are using boot2docker then first find ip address using $ boot2docker ip and the use the ip http://<host_ip>:5000

### Running locally

1. Setup the virtual environment: `python venv venv`
2. Source the virtual environment: `source ./venv/bin/activate`
3. Install the requirements: `pip install -r requirements.txt`
4. Execute the main.py: `python src/main.py --config local_dev.json`

import json
import logging
import os
import uuid
from datetime import datetime
from pathlib import *
from typing import Any, Optional, Type
from http.client import HTTPConnection

from ..utils.ssm_parameter_store import SSMParameterStore
from ..utils.typing import OptionalDict

from ruamel.yaml import YAML
import requests

# Environment vars
ENV = os.environ.get('ENV', 'dev')
PATH = os.environ.get('LAMBDA_TASK_ROOT', '')

# Get aws config from env
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', None)
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', None)
AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION', "us-east-1")
COLLABS_SERVICE_API_HOST = os.environ.get('COLLABS_SERVICE_API_HOST', None)
HYPERLINK_SERVICE_API_HOST = os.environ.get('HYPERLINK_SERVICE_API_HOST', None)

# Create custom logger, handler, and formatter
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

# Prepare reading YAML files into streams
yaml = YAML()

def load_ssm_config(path):
  """load_ssm_config
  Reads SSM configuration from provided YAML file.
  This file should be available in lambda_function/ during the build.
  """
  params = {}
  try:
    if path:
      LOGGER.info('loading SSM configuration from file {}'.format(path))
      with open(os.path.join(PATH, path)) as file:
          data = yaml.load(file)
          for item, val in data.items():
              params[item] = val
    else:
      # if loading SSM configuration from Lambda task directory
      LOGGER.info('loading SSM configuration from file')
      with open(os.path.join(PATH, "/var/task/lambda_function/ssm-params.yml")) as file:
          data = yaml.load(file)
          for item, val in data.items():
              params[item] = val
  except Exception as e:
    LOGGER.exception(e.message)

  # If the environment is not local, load the params from SSM
  if os.environ.get('AWS_SAM_LOCAL', False) is False:
    LOGGER.info('requesting SSM params from store')
    param_store = SSMParameterStore(ENV, region_name=AWS_DEFAULT_REGION)
    response = param_store.fetch_many(
        required=list(params.values())
    )
    values = list(response.values())
    return {
      "COLLABS_SERVICE_API_HOST": values[0],
      "HYPERLINK_SERVICE_API_HOST": values[1]
    }
  # If running locally, you must provide the SSM config as an ENV variable
  # This can be provided by running sam local invoke with the --env-vars <local.json> option
  else:
    LOGGER.info('environment is local; loading SSM params from environment')
    return {
      "COLLABS_SERVICE_API_HOST": COLLABS_SERVICE_API_HOST,
      "HYPERLINK_SERVICE_API_HOST": HYPERLINK_SERVICE_API_HOST
    }
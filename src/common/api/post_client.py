import json
import logging
import os
import sys
import uuid
import urllib.parse
from datetime import datetime
from pprint import pprint

import requests
from ruamel.yaml import YAML

from ..utils.ssm_config import load_ssm_config
from ..utils.typing import OptionalDict
from ..client import APIClient

# Create custom logger, handler, and formatter
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

# Environment vars
ENV = os.environ.get('ENV', 'dev')
PATH = os.environ.get('LAMBDA_TASK_ROOT', '')

# Get aws config from env
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', None)
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', None)
AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION', "us-east-1")

# API Environment Variables
POST_SERVICE_API_HOST = os.environ.get('POST_SERVICE_API_HOST', None)

class PostClient(APIClient):
  def __init__(self):
    self.base_url = POST_SERVICE_API_HOST
    super().__init__()

  def get_links_for_post_id(self, post_id):
    try:
      url = '%s/v1/posts/%s/rstyle_links'  % (self.base_url, post_id)
      response = self.get(url)
      data = response.json()
      LOGGER.debug(data)
      return data
    
    except (requests.ConnectionError, requests.Timeout) as e:
      raise e

    except requests.HTTPError as e:
      LOGGER.exception(e.response.content)
      raise e

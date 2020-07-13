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
HYPERLINK_SERVICE_API_HOST = os.environ.get('HYPERLINK_SERVICE_API_HOST', None)

# Prepare reading YAML files into streams
yaml = YAML()

class HyperlinkClient(APIClient):
  def __init__(self):
    # cfg = load_ssm_config()
    # self.base_url = cfg.get('HYPERLINK_SERVICE_API_HOST')
    self.base_url = HYPERLINK_SERVICE_API_HOST
    super().__init__()

  def get_link(self, link):
      """
      Calls off to hyperlink client to request hyperlink's metric data for link. From this data, 
      we specifically need the advertiser_id and hyperlink_id (for future reference).
      
      Advertiser onboards with rS, they get an advertiser ID.  This is their source and redirect ID.  
      If the advertiser decides to start a new program for a new geography, or they switch affiliate networks, we grant them a new ID.  
      For links created before the program change, the old ID is the source, the new ID is the redirect.  For new links, 
      both the source and redirect ID will be the same (the new ID).

      Yoink is also able to change advertiser IDs based on parameters found in the link or for other reasons, if desired.
      The Yoink ID changes are always reflected in the redirect_advertiser field.

      Notably, Hyperlink provides four advertiser_id fields in the response:
      * source_advertiser - the original advertiser ID created for the advertiser when onboarded.
      * migration_advertiser - it appears this one was created for a migration? Not relevant here.
      * redirect_advertiser - the advertiser ID used for redirecting the user. This ID is used for advertisers who have switched
        * their affiliate networks and have been granted a new ID. This ID is used for all new rstyle links.
      * yoink_advertiser - the advertiser ID created by Yoink (not always provided).
      Arguments:
        link (string) -- The rstyle link following this format: https://rstyle.me/:id
      Returns: 
        advertiser_id (string) -- The advertiser ID for the rstyle metric.
      """
      try:
        encoded_link = urllib.parse.quote(link)
        url = '%s/api/links/%s'  % (self.base_url, encoded_link)
        response = self.get(url)
        data = response.json()
        LOGGER.debug(data)
        return data
      
      except (requests.ConnectionError, requests.Timeout) as e:
        raise e

      except requests.HTTPError as e:
        LOGGER.exception(e.response.content)
        raise e

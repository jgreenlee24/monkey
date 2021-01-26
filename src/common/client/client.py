import datetime
import json
import logging
import requests

from typing import Any, Optional, Type
from http.client import HTTPConnection
from ..utils.typing import OptionalDict

# Create custom logger, handler, and formatter
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

# Hooks
def check_for_errors(resp, *args, **kwargs):
  resp.raise_for_status()

class APIClient():
  def __init__(self):
    self.session = requests.Session()
    self.session.hooks['response'] = [check_for_errors]

  def post(self, endpoint: str, data: dict, params: OptionalDict = None, **kwargs):
    """Send data and return response data from POST endpoint."""
    LOGGER.info("POST %s with %s", endpoint, data)
    return self.session.post(endpoint, data=data, params=params, **kwargs)

  def get(self, endpoint: str, params: OptionalDict = None, **kwargs):
    """Return response data from GET endpoint."""
    LOGGER.info("GET %s", endpoint)
    return self.session.get(endpoint, params=params, **kwargs)

  def put(self, endpoint: str, data: dict, params: OptionalDict = None, **kwargs):
    """Send data to overwrite resource and return response data from PUT endpoint."""
    LOGGER.info("PUT %s with %s", endpoint, data)
    return self.session.put(endpoint, data=data, params=params, **kwargs)

  def patch(self, endpoint: str, data: dict, params: OptionalDict = None, **kwargs):
    """Send data to update resource and return response data from PATCH endpoint."""
    LOGGER.info("PATCH %s with %s", endpoint, data)
    return self.session.patch(endpoint, data=data, params=params, **kwargs)

  def delete(self, endpoint: str, params: OptionalDict = None, **kwargs):
    """Remove resource with DELETE endpoint."""
    LOGGER.info("DELETE %s", endpoint)
    return self.session.delete(endpoint, params=params, **kwargs)

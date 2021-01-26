import json
import logging
import os
import re
import sys
import traceback
import uuid
from datetime import datetime, timedelta
from ..utils.ssm_parameter_store import SSMParameterStore
from ..utils.typing import Map

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

# Environment vars
HYPERLINK_CASSANDRA_DB = os.environ.get('HYPERLINK_CASSANDRA_DB', None)
HYPERLINK_CASSANDRA_HOST = os.environ.get('HYPERLINK_CASSANDRA_HOST', None)
HYPERLINK_CASSANDRA_PORT = os.environ.get('HYPERLINK_CASSANDRA_PORT', None)
HYPERLINK_CASSANDRA_USER = os.environ.get('HYPERLINK_CASSANDRA_USER', None)
HYPERLINK_CASSANDRA_PASSWORD = os.environ.get('HYPERLINK_CASSANDRA_PASSWORD', None)
ENV = os.environ.get('ENV', 'dev')

# Get aws config from env
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', None)
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', None)
AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION', "us-east-1")

# Database connection config
DB_CONFIG = {
  'host': ['192.168.8.19','192.168.8.41','192.168.8.72'],
  'user': HYPERLINK_CASSANDRA_USER,
  'password': HYPERLINK_CASSANDRA_PASSWORD,
  'db': HYPERLINK_CASSANDRA_DB,
  'port': HYPERLINK_CASSANDRA_PORT
}

# Create custom logger, handler, and formatter
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class LinksConnector():
  def __init__(self):
    self.connect_hyperlink_db()
    super().__init__()

  def add_link(self, data):
    """
    Save RStyle Link - persists the rstyle link data to the Cassandra db table `links`
    Arguments:
      data [JSON]: serialized JSON data for RStyle Link
    """
    try:
      link = Map(data)
      product = Map(link.item)
      publisher = Map(link.publisher)

      sql = "INSERT INTO links (id, link_url, product_id, product_id_v2, product_name, product_price, product_sku, \
          product_type, publisher_id, redirect_url, version) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
      
      self.session.execute(sql, (link.id, link.url,product.id,product.product_id_v2,product.name,product.price,product.sku,
          product.product_type,publisher.Id,link.redirect_url,link.version))
    
    except Exception as err:
      LOGGER.error('error in persisting rstyle link for url {}'.format(link.url), exc_info=True)
      raise err

  def connect_hyperlink_db(self, **kwargs):
    """
    Connect Hyperlink DB - Attempts to esablish a connection with the Hyperlink Cassandra Database.
    Arguments:
      cfg (dict): optional DB configuration
    Raises:
      Exception: Failure to connect
    Returns:
      self {[cassandra.cluster]} -- A Cannasndra Cluster connection pool
    """
    cfg = kwargs.get('cfg', None)
    if env_vars_provided():
      try:
        LOGGER.debug("db connection details: {}".format(DB_CONFIG))
        auth_provider = PlainTextAuthProvider(username=DB_CONFIG['user'], password=DB_CONFIG['password'])
        cluster = Cluster(DB_CONFIG['host'],auth_provider=auth_provider,port=DB_CONFIG['port'])
        self.session = cluster.connect(DB_CONFIG['db'],wait_for_all_pools=True)
        self.session.execute("USE %s" % DB_CONFIG['db'])
        return self.session
      except Exception as err:
        LOGGER.error('failed to connect to Hyperlink Cassandra database: {}'.format(err))
        raise err
    elif cfg is not None:
      try:
        LOGGER.debug("db connection details: {}".format(cfg))
        cluster = Cluster([cfg.host],port=cfg.port)
        self.session = cluster.connect(cfg.db,wait_for_all_pools=True)
        self.session.execute("USE %s" % cfg.db)
        return self.session
      except Exception as err:
        LOGGER.error('failed to connect to Hyperlink Cassandra database: {}'.format(err))
        raise err
    else:
      raise Exception("Missing required environment variables")

def env_vars_provided():
  """env_vars_provided
  Returns:
      Boolean -- Whether the expected environment variables have been provided.
  """
  return HYPERLINK_CASSANDRA_HOST and HYPERLINK_CASSANDRA_USER and HYPERLINK_CASSANDRA_PASSWORD

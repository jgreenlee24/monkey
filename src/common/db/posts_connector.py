import json
import logging
import os
import re
import sys
import traceback
import uuid
from datetime import datetime, timedelta
from ..utils.ssm_parameter_store import SSMParameterStore

import boto3
import pymysql

# Environment vars
POST_DB_NAME = os.environ.get('POST_DB_NAME', None)
POST_SERVICE_MYSQL_HOST = os.environ.get('POST_SERVICE_MYSQL_HOST', None)
POST_SERVICE_MYSQL_PORT = os.environ.get('POST_SERVICE_MYSQL_PORT', None)
POST_SERVICE_MYSQL_USER = os.environ.get('POST_SERVICE_MYSQL_USER', None)
POST_SERVICE_MYSQL_PASSWORD = os.environ.get('POST_SERVICE_MYSQL_PASSWORD', None)
ENV = os.environ.get('ENV', 'dev')

# Database connection config
DB_CONFIG = {
  'host': POST_SERVICE_MYSQL_HOST,
  'user': POST_SERVICE_MYSQL_USER,
  'password': POST_SERVICE_MYSQL_PASSWORD,
  'db': POST_DB_NAME,
  'charset': 'utf8mb4',
  'cursorclass': pymysql.cursors.DictCursor
}

# Create custom logger, handler, and formatter
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class PostConnector():
  def __init__(self, cfg=None):
    # cfg = load_ssm_config()
    self.connect_post_db(cfg)
    super().__init__()

  def execute(self, query, data=None):
    """
    Executes a given query against the posts database.
    Arguments:
      query (string) -- SQL template string to execute
      data ()
    Returns:
      result (list of tuples)
    """
    try:
      with self.cnx.cursor() as cursor:
        if data is not None:
          cursor.execute(query, data)
        else:
          cursor.execute(query)
        result = cursor.fetchall()
        if result is None:
          raise Exception('not found')
        return result
    except Exception as err:
      LOGGER.error('running query {}'.format(query), exc_info=True)
      raise err

  def update_batch_posts(self, post_ids, data):
    """
    Given an array of post IDs, update the posts with the provided batch payload.
    Arguments:
      post_id (string) -- Unique identifier for the post
      data ()
    Returns:
      result (list of tuples)
    """
    try:
      with self.cnx.cursor() as cursor:
        sql = "UPDATE reporting_start_time, reporting_end_time where post_id in %s;"
        cursor.execute(sql, post_ids)
        result = cursor.fetchall()
        if result is None:
          raise Exception('not found')
        return result
    except Exception as err:
      LOGGER.error('updating posts {}'.format(post_ids), exc_info=True)
      raise err

  def get_rstyle_links_for_post_id(self, post_id):
    """
    Get Rstyle Links by Post ID - Queries the `rstyle_links` table in the Post DB
    Arguments:
      post_id (string) -- Unique identifier for the post
    Returns:
      result (list of tuples)
    """
    try:
      with self.cnx.cursor() as cursor:
        sql = "SELECT url FROM rstyle_links where post_id=%s;"
        cursor.execute(sql, post_id)
        result = cursor.fetchall()
        if result is None:
          raise Exception('not found')
        return result
    except Exception as err:
      LOGGER.error('error getting rstyle_links for post id {}'.format(post_id), exc_info=True)
      raise err

  def connect_post_db(self, cfg):
    """
    Connect Post DB - Attempts to esablish a connection with the Posts Database.
    Arguments:
      cfg (dict): optional DB configuration
    Raises:
      Exception: Failure to connect
    Returns:
      self {[pymsql.Connection]} -- A pymsql.Connection pool
    """
    if cfg is not None:
      try:
        cnx = cnx_from_config(cfg)
        LOGGER.debug("db connection details: {}".format(cnx))
        self.cnx = pymysql.connect(**cnx)
        return self.cnx
      except Exception as err:
        LOGGER.error('failed to connect to posts database: {}'.format(err))
        raise err
    elif env_vars_provided():
      try:
        LOGGER.debug("db connection details: {}".format(DB_CONFIG))
        self = pymysql.connect(**DB_CONFIG)
        return self
      except Exception as err:
        LOGGER.error('failed to connect to posts database: {}'.format(err))
        raise err
    else:
      raise Exception("Missing required environment variables")

def cnx_from_config(cfg):
  """Connections from Configuration
  Args:
      cfg ([Map]): parsed JSON from file
  Returns:
      [type]: [description]
  """
  return {
    'host': cfg['POST_SERVICE_MYSQL_HOST'],
    'user': cfg['POST_SERVICE_MYSQL_USER'],
    'password': cfg['POST_SERVICE_MYSQL_PASSWORD'],
    'db': cfg['POST_DB_NAME'],
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
  }

def env_vars_provided():
  """env_vars_provided
  Returns:
      Boolean -- Whether the expected environment variables have been provided.
  """
  return POST_SERVICE_MYSQL_HOST and POST_SERVICE_MYSQL_USER and POST_SERVICE_MYSQL_PASSWORD

def load_ssm_config():
  """load_ssm_config
  """
  param_store = SSMParameterStore(ENV, region_name=AWS_DEFAULT_REGION)
  params = param_store.fetch_many(
      required=[
        '/rds/rs-post-service/db', 
        '/rds/rs-post-service/host', 
        '/rds/rs-post-service/port', 
        '/rds/rs-post-service/rw-user', 
        '/rds/rs-post-service/rw-password'
      ]
  )
  return params
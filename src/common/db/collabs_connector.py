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
COLLABS_DB_NAME = os.environ.get('COLLABS_DB_NAME', None)
COLLABS_SERVICE_MYSQL_HOST = os.environ.get('COLLABS_SERVICE_MYSQL_HOST', None)
COLLABS_SERVICE_MYSQL_PORT = os.environ.get('COLLABS_SERVICE_MYSQL_PORT', None)
COLLABS_SERVICE_MYSQL_USER = os.environ.get('COLLABS_SERVICE_MYSQL_USER', None)
COLLABS_SERVICE_MYSQL_PASSWORD = os.environ.get('COLLABS_SERVICE_MYSQL_PASSWORD', None)
AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION', "us-east-1")
ENV = os.environ.get('ENV', 'dev')

# Database connection config
DB_CONFIG = {
  'host': COLLABS_SERVICE_MYSQL_HOST,
  'user': COLLABS_SERVICE_MYSQL_USER,
  'password': COLLABS_SERVICE_MYSQL_PASSWORD,
  'db': COLLABS_DB_NAME,
  'charset': 'utf8mb4',
  'cursorclass': pymysql.cursors.DictCursor
}

# Create custom logger, handler, and formatter
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class CollabsConnector():
  def __init__(self, cfg=None):
    # cfg = load_ssm_config()
    self.connect_collabs_db(cfg)
    super().__init__()

  def execute(self, query, data=None):
    """
    Executes a given query against the collaborations database.
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

  def update_campaign_reporting_dates(self, campaign_ids, data):
    """
    Given an array of campaign IDs, update the campaign reporting start date to match the campaign start date
    and update the campaign reporting end date to match the campaign start date + 6 weeks.
    Arguments:
      campaign_ids (string) -- List of unique identifiers for campaigns
      data ()
    Returns:
      result (list of tuples)
    """
    try:
      with self.cnx.cursor() as cursor:
        sql = "UPDATE reporting_start_time, reporting_end_time where campaign_id in %s VALUES (%s, %s);;"
        cursor.execute(sql, campaign_ids)
        result = cursor.fetchall()
        if result is None:
          raise Exception('not found')
        return result
    except Exception as err:
      LOGGER.error('updating campaigns {}'.format(campaign_ids), exc_info=True)
      raise err

  def get_advertiser_ids(self, brand_id):
    """
    Get Advertiser ID - Queries the `brand_advertisers` table in the Collabs 
    Arguments:
      brand_id [string] -- Returns a list of the associated advertiser IDs for the given brand ID.
    """
    try:
      with self.cnx.cursor() as cursor:
        sql = "SELECT advertiser_ids FROM brand_advertisers WHERE brand_id=%s;"
        cursor.execute(sql.format(brand_id))
        result = cursor.fetchone()
        if result is None:
          raise Exception('not found')
        return result
    except Exception as err:
      LOGGER.error('error getting advertiser ids for brand id {}'.format(brand_id), exc_info=True)
      raise err

  def get_brand_id(self, collab_id):
    """
    Get Brand ID by Collaboration ID - Queries the `collaborations` table in the Collabs 
    Arguments:
      brand_id (string) -- Returns the brand ID for the provided collaboration ID.
    """
    try:
      with self.cnx.cursor() as cursor:
        sql = "SELECT brand_id FROM collaborations where id=%s;"
        cursor.execute(sql, collab_id)
        result = cursor.fetchone()
        if result is None:
          raise Exception('not found')
        return result
    except Exception as err:
      LOGGER.error('error getting brand id for collaboration id {}'.format(collab_id), exc_info=True)
      raise err

  def get_brand_id_by_advertiser_id(self, advertiser_id):
    """
    Get Brand ID by Advertiser ID - Queries the `brand_advertisers` table in the Collabs 
    Arguments:
      brand_id (string) -- Returns the brand ID for the provided advertiser ID.
    """
    try:
      with self.cnx.cursor() as cursor:
        sql = "SELECT `brand_id` FROM `collaborations`.`brand_advertisers` WHERE `advertiser_ids` LIKE '%{}%';"
        cursor.execute(sql.format(advertiser_id))
        result = cursor.fetchone()
        if result is None:
          raise Exception('not found')
        return result
    except Exception as err:
      LOGGER.error('error getting brand id for advertiser id {}'.format(advertiser_id), exc_info=True)
      raise err

  def get_collaboration_id_by_obligation_id(self, obligation_id):
    """
    Get Collaboration by Obligation ID - Queries the `obligations` table in the Collabs 
    Arguments:
      collaboration_id (string) -- Returns the collab ID for the provided obligation ID.
    """
    try:
      with self.cnx.cursor() as cursor:
        sql = "SELECT collaboration_id as id FROM obligations WHERE id = %s;"
        cursor.execute(sql, obligation_id)
        result = cursor.fetchone()
        if result is None:
          raise Exception('not found')
        return result
    except Exception as err:
      LOGGER.error('error getting collab id for obligation id {}'.format(obligation_id), exc_info=True)
      raise err

  def get_obligation_id_by_post_id(self, post_id):
    """
    Get Obligation by Post ID - Returns the obligation for the provided Post ID.
    Arguments:
    post_id [Integer]: ID uniquely identifying the Post
    Returns [Integer]: The ID uniquely identifying the Obligation
    """
    try:
      with self.cnx.cursor() as cursor:
        sql = "SELECT id FROM obligations WHERE post_id=%s;"
        cursor.execute(sql, post_id)
        result = cursor.fetchone()
        if result is None:
          raise Exception('not found')
        return result
    except Exception as err:
      LOGGER.error('error getting obligation for post id {}'.format(post_id), exc_info=True)
      raise err

  def save_rstyle_links_for_obligation_id(self, rstyle_links, obligation_id):
    """
    Save RStyle Link For Obligation ID - persists the rstyle links and obligation id pair
    to the `obligation_rstyle_links` table in Collaborations 
    Arguments:
      rstyle_links [String]: CSV string containing rstyle links
      obligation_id [Integer]: ID uniquely identifying the Obligation
    """
    try:
      with self.cnx.cursor() as cursor:
        sql = "INSERT INTO obligation_rstyle_links (obligation_id, rstyle_links) VALUES (%s, %s);"
        cursor.execute(sql, (obligation_id, rstyle_links))
        cursor.commit()
    except Exception as err:
      LOGGER.error('error in persisting rstyle links for obligation id {}'.format(obligation_id), exc_info=True)
      raise err

  def connect_collabs_db(self, cfg):
    """
    Connect Collabs DB - Attempts to esablish a connection with the Collaborations Database.
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
        LOGGER.error('failed to connect to collaborations database: {}'.format(err))
        raise err
    elif env_vars_provided():
      try:
        LOGGER.debug("db connection details: {}".format(DB_CONFIG))
        self = pymysql.connect(**DB_CONFIG)
        return self
      except Exception as err:
        LOGGER.error('failed to connect to collaborations database: {}'.format(err))
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
    'host': cfg['COLLABS_SERVICE_MYSQL_HOST'],
    'user': cfg['COLLABS_SERVICE_MYSQL_USER'],
    'password': cfg['COLLABS_SERVICE_MYSQL_PASSWORD'],
    'db': cfg['COLLABS_DB_NAME'],
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
  }

def env_vars_provided():
  """env_vars_provided
  Returns:
      Boolean -- Whether the expected environment variables have been provided.
  """
  return COLLABS_SERVICE_MYSQL_HOST and COLLABS_SERVICE_MYSQL_USER and COLLABS_SERVICE_MYSQL_PASSWORD

def load_ssm_config():
  """load_ssm_config
  """
  param_store = SSMParameterStore(ENV, region_name=AWS_DEFAULT_REGION)
  params = param_store.fetch_many(
      required=[
        '/rds/collaboration-service/db', 
        '/rds/collaboration-service/host', 
        '/rds/collaboration-service/port', 
        '/rds/collaboration-service/rw-user', 
        '/rds/collaboration-service/rw-password'
      ]
  )
  return params
import argparse
import json
import logging
import os
import re
import sys
import traceback
import uuid
import requests
from datetime import timedelta

from common.db.collabs_connector import *
from common.db.posts_connector import *

# Create custom logger, handler, and formatter
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

def main():
  """ main
  Queries the collaboration-service for improperly formatted reporting_end_time values
  and corrects those values by using the campaign end_time value.
  """
  parser = argparse.ArgumentParser(description = "Command arguments for reporting_date_sync")
  parser.add_argument("-c", "--config", help = "Path for config JSON file", required = False, default = "")
  args = parser.parse_args()
  cfg = None

  if args.config:
    try:
      with open(args.config) as f:
        cfg = json.load(f)
    except Exception as error: 
      LOGGER.error('error processing config: {}'.format(error))
  
  # main logic
  try:
    # setup db connections
    collabs_cnx = CollabsConnector(cfg)
    posts_cnx = PostConnector(cfg)

    # run jobs
    # fix_reporting_dates_0001(collabs_cnx, posts_cnx)
    fix_reporting_dates_null(collabs_cnx, posts_cnx)

  except Exception as error:
    print('error in main loop {}'.format(error))

  print("finished")

def fix_reporting_dates_null(collabs_cnx, posts_cnx):
  """
   Fix posts where reporting_start_time and reporting_end_time are NULL
   within the currently relevant reporting period (> 9/1/2020).
  """

  # get all post IDs where reporting_end_date and reporting_start_date are null:
  posts = posts_cnx.execute("""
    SELECT * FROM posts 
    WHERE status != 'DELETED' 
    AND reporting_end_time IS NULL 
    AND (channel != 'LTK' AND channel != 'BLOG' AND channel != 'NO_CHANNEL') 
    AND created_at >= '2020-09-01 00:00:00'
  """.replace('\n','').replace('\t',''))
  if len(posts) == 0:
    print('no posts found where reporting_end_time is NULL')
    return

  print('posts count: ' + str(len(posts)))

  # get the campaigns for these posts by joining w/ obligations
  result = map(lambda p: p['id'], posts) 
  post_ids = ','.join('"{0}"'.format(w) for w in list(result))
  query = """
    SELECT campaigns.*, obligations.post_id as post_id 
    FROM obligations JOIN campaigns ON campaigns.id = obligations.campaign_id 
    WHERE obligations.post_id IN ({})
  """.format(post_ids).replace('\n','').replace('\t','')

  obligations = collabs_cnx.execute(query)
  print('obligations count: ' + str(len(obligations)))
  
  # check to see which posts are not tied to obligations
  obl_post_ids = map(lambda o: o['post_id'], obligations)
  obl_post_ids = ','.join('"{0}"'.format(w) for w in list(obl_post_ids))
  print(diff(obl_post_ids.split(','), post_ids.split(',')))

  # update the posts' reporting_end_time
  values = {}
  d = timedelta(weeks=6)
  for o in obligations:
    # store the start_date and end_date as a tuple mapped by post_id
    values[o['post_id']] = (
      (o['start_date'] + d).strftime("%Y-%m-%d %H:%M:%S"), 
      (o['end_date'] + d).strftime("%Y-%m-%d %H:%M:%S")
    )

  vals = [(v[0], v[1], k) for k, v in values.items()] 
  posts_cnx.executemany("UPDATE posts SET reporting_start_time = %s, reporting_end_time = %s WHERE id = %s", vals)

  print('successfully updated posts where reporting times are NULL')

def fix_reporting_dates_0001(collabs_cnx, posts_cnx):
  """
  Fix posts where reporting_end_time like %0001%.
  This is related to a problem introduced to the collaboration-service on 9/23/2020.
  """

  # get all post IDs where campaign reporting_end_date is invalid:
  posts = posts_cnx.execute("SELECT * FROM posts WHERE reporting_end_time LIKE '%0001%';")
  if len(posts) == 0:
    print('no posts found where reporting_end_time like 0001')
    return

  # get the campaigns for these posts by joining w/ obligations
  result = map(lambda p: p['id'], posts) 
  post_ids = ','.join('"{0}"'.format(w) for w in list(result))
  query = """
    SELECT campaigns.*, obligations.post_id as post_id 
    FROM obligations JOIN campaigns ON campaigns.id = obligations.campaign_id 
    WHERE obligations.post_id IN ({})
  """.format(post_ids).replace('\n','').replace('\t','')
  campaigns = collabs_cnx.execute(query)

  # update the posts' reporting_end_time
  values = {}
  d = timedelta(weeks=6)
  for c in campaigns:
    values[c['post_id']] = (c['end_date'] + d).strftime("%Y-%m-%d %H:%M:%S")

  vals = [(v, k) for k, v in values.items()] 
  posts_cnx.executemany("UPDATE posts SET reporting_end_time = %s WHERE id = %s", vals)

  print('successfully updated posts where reporting_end_time like 0001')

def diff(li1, li2):
  return (list(list(set(li1)-set(li2)) + list(set(li2)-set(li1))))

if __name__ == "__main__":
  main()

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
    collabs_cnx = CollabsConnector(cfg)
    posts_cnx = PostConnector(cfg)

    # get all post IDs where campaign reporting_end_date is invalid:
    posts = posts_cnx.execute("SELECT * FROM posts WHERE reporting_end_time LIKE '%0001%';")
    if len(posts) == 0:
      print('no posts found')
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

    print('successfully updated posts')

  except Exception as error:
    print('error in main loop {}'.format(error))

  print("finished")

if __name__ == "__main__":
  main()

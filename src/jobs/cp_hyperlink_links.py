import argparse
import json
import logging
import os
import re
import sys
import traceback
import uuid
import requests

from common.api.hyperlink_client import HyperlinkClient
from common.db.links_connector import LinksConnector
from common.db.posts_connector import PostConnector

# Create custom logger, handler, and formatter
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

def main():
  """ main
  Given an rstyle link as a client argument, request the link data from Hyperlink API (in prod)
  and save this data to QA Cassandra `links` table.
  """
  parser = argparse.ArgumentParser(description = "Command arguments for cp_hyperlink_links")
  parser.add_argument("-c", "--config", help = "Path for config JSON file", required = False, default = "")
  parser.add_argument("-l", "--link", help = "Unencrypted rstyle link url", required = False, default = "")
  parser.add_argument("-p", "--post", help = "Post identifier", required = False, default = "")
  args = parser.parse_args()

  if args.config:
    try:
      with open(args.config) as f:
        data = json.load(f)
    except Exception as error: 
      LOGGER.error('error processing config: {}'.format(error), exc_info=True)
  
  # main logic
  try:
    hyperlink = HyperlinkClient()
    posts_cnx = PostConnector()
    links_cnx = LinksConnector()

    if args.post:
      links = posts_cnx.get_rstyle_links_for_post_id(args.post)
      if len(links) == 0:
        print('no links found for post id {} \n'.format(args.post))
      else:
        print('found {} links for post id {} \n'.format(links, args.post))
      for val in links:
        link = hyperlink.get_link(val['url'])
        print('response {} from hyperlink \n', link)
        links_cnx.add_link(link)
        print('successfully added link {} to QA environment \n'.format(val))
    
    elif args.link:
      link = hyperlink.get_link(args.link)
      links_cnx.add_link(link)

  except Exception as error:
    print('error in main loop {}'.format(error), exc_info=True)

  print("finished")

if __name__ == "__main__":
  main()
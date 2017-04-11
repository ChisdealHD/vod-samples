#!/usr/bin/python

'''
Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

    http://aws.amazon.com/apache2.0/

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
'''

import httplib2
import os
import sys
import subprocess
import json
import requests
import time

from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

TWITCH_CLIENT_ID = "<YOUR CLIENT ID HERE>"
TWITCH_VERSION_HEADER = "application/vnd.twitchtv.v4+json"

YOUTUBE_CLIENT_SECRETS_FILE = "client_secrets.json"
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

MISSING_CLIENT_SECRETS_MESSAGE = "Missing client_secrets.json. See: https://developers.google.com/api-client-library/python/guide/aaa_client_secrets"

CHUNKSIZE = 10 * 1024 * 1024 # 10MB chunk size for video parts

def get_authenticated_service(args):
  flow = flow_from_clientsecrets(YOUTUBE_CLIENT_SECRETS_FILE,
    scope=YOUTUBE_READ_WRITE_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))

def get_youtube_video_info(video_id):
  print 'Getting metadata for YouTube video ' + video_id + '...'
  videos_list_response = youtube.videos().list(id=video_id, part='snippet').execute()

  if not videos_list_response["items"]:
    print "Video '%s' was not found." % video_id
    sys.exit(1)

  video_info = videos_list_response["items"][0]["snippet"]
  print "Title: " + video_info["title"]
  return video_info["title"], video_info["description"], video_info["tags"]

def download_from_youtube(video_id):
  print "Downloading video from YouTube..."
  subprocess.check_call(["./youtube-dl", "--quiet", "--id", video_id])
  return video_id + ".mp4"

def get_channel_name(twitch_auth_token):
  url = 'https://api.twitch.tv/kraken/user'
  headers = {'Authorization': 'OAuth ' + twitch_auth_token,
             'Accept': TWITCH_VERSION_HEADER,
             'Client-ID': TWITCH_CLIENT_ID }  
  r = requests.get(url, headers=headers)
  user = r.json()
  return user['name']

def create_twitch_video(title, description, tags, twitch_auth_token):
  print 'Creating video on Twitch...'
  url = 'https://api.twitch.tv/kraken/videos'
  payload = {'channel_name': get_channel_name(twitch_auth_token),
             'title': title,
             'description': description,
             'tags': tags }  
  headers = {'Authorization': 'OAuth ' + twitch_auth_token,
             'Accept': TWITCH_VERSION_HEADER,
             'Client-ID': TWITCH_CLIENT_ID,
             'Content-Type': 'application/json' }
  r = requests.post(url, json=payload, headers=headers)
  video = r.json()
  return video["upload"]["url"], video["upload"]["token"]

def upload_to_twitch(filename, upload_url, upload_token):
  print "Uploading " + filename + " to Twitch via " + upload_url + ", " + str(CHUNKSIZE) + " bytes at a time..."  

  file = open(filename, 'rb')
  index = 0
  while 1:
    chunk = file.read(CHUNKSIZE)
    if not chunk: break
    index += 1
    headers = {'Accept': TWITCH_VERSION_HEADER,
               'Client-ID': TWITCH_CLIENT_ID,
               'Content-Length': str(len(chunk)) }
    params = {'part': index,
               'upload_token': upload_token }
    r = requests.put(upload_url, params=params, data=chunk, headers=headers)
    print 'Completed uploading part ' + str(index)
  file.close()

  headers = {'Accept': TWITCH_VERSION_HEADER,
             'Client-ID': TWITCH_CLIENT_ID }
  params = {'upload_token': upload_token }
  r = requests.post(upload_url + '/complete', params=params, headers=headers)
  return

def get_youtube_video_ids(playlist_id):
  print 'Getting video ids for YouTube playlist ' + playlist_id + '...'
  playlist_items_response = youtube.playlistItems().list(playlistId=playlist_id, part='snippet',maxResults=50).execute()

  if not playlist_items_response["items"]:
    print 'Playlist %s was not found.' % playlist_id
    sys.exit(1)

  video_ids = []
  for playlist_item in playlist_items_response["items"]:
    video_ids.append(playlist_item["snippet"]["resourceId"]["videoId"])

  return video_ids

if __name__ == "__main__":
  start = time.clock()

  argparser.add_argument("--video-id", help="ID of Youtube video to download.",
    required=False)
  argparser.add_argument("--playlist-id", help="ID of Youtube playlist to download.",
    required=False)  
  argparser.add_argument("--twitch-token", help="OAuth Token for Twitch",
    required=True)  
  args = argparser.parse_args()

  if not args.video_id and not args.playlist_id:
    print 'Must provide either YouTube video or playlist ID'
    sys.exit(1)

  youtube = get_authenticated_service(args)
  if args.video_id:
    title, description, tags = get_youtube_video_info(args.video_id)
    filename = download_from_youtube(args.video_id)
    upload_url, upload_token = create_twitch_video(title, description, tags, args.twitch_token)
    upload_to_twitch(filename, upload_url, upload_token)
  else:
    video_ids = get_youtube_video_ids(args.playlist_id)
    for video_id in video_ids:
      title, description, tags = get_youtube_video_info(video_id)
      filename = download_from_youtube(video_id)
      upload_url, upload_token = create_twitch_video(title, description, tags, args.twitch_token)
      upload_to_twitch(filename, upload_url, upload_token)

  end = time.clock()
  duration = end - start
  print "Transfer complete, total duration: " + str(duration) + " second(s)"
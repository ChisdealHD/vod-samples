# Twitch VOD Upload Python Sample
Here you will find a simple Python application illustrating how to upload a VOD to Twitch using the [VOD Upload API](https://dev.twitch.tv/docs/v5/guides/video-upload/).  This sample uses [youtube-dl](https://rg3.github.io/youtube-dl/) to download videos, so you can easily copy your videos  to Twitch.

## Installation
1. Download youtube-dl for your system at [https://rg3.github.io/youtube-dl/download.html] and place it in the same directory as the sample.
2. Use pip or easy_install to install the Google API Python Client
```sh
$ pip install google-api-python-client
```
3. [Register an OAuth2 Application on Google.](https://cloud.google.com/console) You will download a client_secrets.json file to place in the same directory as the sample.
4. [Register an OAuth2 Application on Twitch.](https://twitch.tv/settings/connections) Set the Client-ID in the sample python script, and use this application to authenticate against the API.

## Usage
To run the sample, you will need to provide an OAuth access token with the channel_editor scope.  You can reference an authentication sample to accomplish this.

```sh
$ python vod-copy.py --video-id <video-id> --twitch-token <token>
```

You will specify a video ID OR a playlist ID

* Video ID - The ID of the video you want to upload, this will appear in the URL of the video
* Playlist ID - The ID of the video playlist you want to upload, this will appear in the URL of the playlist
* Twitch Token - Your OAuth Token with channel_editor scope.

## License

Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

    http://aws.amazon.com/apache2.0/

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License. 

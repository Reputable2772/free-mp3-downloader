# Free MP3 Downloader

Automatically downloads and syncs your Spotify Playlist with free-mp3-download.net.

### Instructions
Install Python, set up a Virtual Environment.

Clone this repo and install dependencies using

```
git clone https://github.com/Reputable2772/free-mp3-downloader.git
cd free-mp3-downloader
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Setup a .env file containing the following info
```
SPOTIPY_CLIENT_ID= # Required
SPOTIPY_CLIENT_SECRET= # Required
PLAYLIST_ID= # Optional
COOKIE= # Optional
```

Run
```
python3 main.py
```

and answer all the necessary questions. And you're done.


### This repo is licensed under GNU GPLv3
import spotipy
import requests
import urllib
import json
import base64
import os
import asyncio
import aiohttp
from dotenv import load_dotenv
# from spotipy.oauth2 import SpotifyClientCredentials

def checkTrack(track):
    print('Checking', track['track']['name'].strip())
    if os.path.exists(os.path.join('./Music', track['track']['name'].strip() + '.flac')):
        return None

    pushed = False
    song_data_raw = requests.get('https://free-mp3-download.net/search.php?s=' + urllib.parse.quote(track['track']['name'].strip()))
    song_data = json.loads(song_data_raw.content)
    for song in song_data['data']:
        if type(song) is str or song == [] or not song:
            continue
        track_dur = int(track['track']['duration_ms']) // 1000
        deez_dur = song['duration']
        if song['title'].strip().lower() == track['track']['name'].strip().lower():
            if (deez_dur == (track_dur + 0)) \
            or (deez_dur == (track_dur + 1)) \
            or (deez_dur == (track_dur - 1)):
                pushed = song
                break

    if not pushed:
        print("Song \"" + track['track']['name'] + "\" not found.")

    return pushed

async def fetchurl(session, song):
    if type(song) is str or song == [] or not song:
        return None
    song_name_b64 = base64.b64encode(bytes(str(song['title'].strip()), 'utf-8')).decode('utf8')
    headers = {
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Cookie': 'PHPSESSID=' + cookie,
        'DNT': '1',
        'Origin': 'https://free-mp3-download.net',
        'Pragma': 'no-cache',
        'Referer': 'https://free-mp3-download.net/download.php?id=' + str(song['id']) + '&q=' + song_name_b64,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
    }
    json_data = {
        'i': str(song['id']),
        'f': 'flac',
        'h': '',
    }

    print('Downloading', song['title'].strip())

    response = await session.post('https://free-mp3-download.net/dl.php', json=json_data, headers=headers)
    data = await response.text();
    return data;

async def download(session, url):
    if not url:
        return

    bits = await session.get(url)
    split_url = url.split('/')[-1].split('-')
    artist = split_url[0].strip()
    split_url.pop(0)
    name = ' - '.join(split_url).strip()

    if not os.path.exists(os.path.join('./Music')):
        os.mkdir(os.path.join('./Music'))

    with open(os.path.join('./Music', name), 'wb') as f:
        print('Writing', name.split('.')[0])
        async for chunk in bits.content.iter_chunked(1000):
            f.write(chunk)
        print('Downloaded', name.split('.')[0])
        f.close()

async def run_async(list, func):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for task in list:
            tasks.append(func(session, task))
        return await asyncio.gather(*tasks)

def main(arr):
    passed = [];
    failed = [];
    for track in arr:
        status = checkTrack(track)
        if status == False:
            failed.append(track)
        elif type(status) is not bool and type(status) is not None:
            passed.append(status)

    return [passed, failed]

load_dotenv()

limit = int(input('Enter the number of songs to fetch. Should not be > 100.'))
seek = int(input('Enter the song number from where you want to start. Hit 0 if unsure.'))
playlist_id = os.getenv('PLAYLIST_ID').strip()
cookie = os.getenv('COOKIE').strip()

if limit > 100 or not limit:
    print('Invalid limit.')
    exit(1)

if not seek == 0 and not seek:
    print('Invalid seek.')
    exit(1)

if not cookie:
    cookie = str(input('Input cookie. \n')).strip()

if not playlist_id:
    playlist_id = input('Enter playlist id').strip()

spotify = spotipy.Spotify(client_credentials_manager=spotipy.oauth2.SpotifyClientCredentials())
tracks = spotify.playlist_items(playlist_id, None, limit, seek)

info = main(tracks['items'])
links = asyncio.run(run_async(info[0], fetchurl))
asyncio.run(run_async(links, download))

for track in info[1]:
    print('Track', track['track']['name'], 'not found. Retrying.')

inf1 = main(info[1])
links1 = asyncio.run(run_async(inf1[0], fetchurl))
asyncio.run(run_async(links1, download))

for track in inf1[1]:
    print('Track', track['track']['name'], 'not found. Quitting.')

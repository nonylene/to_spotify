import argparse
import json
import os
import re
import sys
import time
from typing import Optional

import colorama
import spotipy
from spotipy.oauth2 import SpotifyOAuth

ALPHANUMERIC = re.compile('^[a-zA-Z0-9]+$')

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=["user-library-modify"]))


def to_query(field_name: str, target: str):
    if ALPHANUMERIC.match(target):
        return f'{field_name}:{target}'
    else:
        return target


def colored(text: str, color: colorama.ansi.AnsiCodes):
    return color + text + colorama.Style.RESET_ALL


def track_term(text: str):
    return colored(text, colorama.Fore.LIGHTYELLOW_EX)


def album_term(text: str):
    return colored(text, colorama.Fore.LIGHTMAGENTA_EX)


def artist_term(text: str):
    return colored(text, colorama.Fore.LIGHTBLUE_EX)


def search_track(track: str, album: str, artist: Optional[str]) -> Optional[str]:
    print(f"QUERY  track: {track_term(track)} album: {album_term(album)} artist: {artist_term(artist or '')}", file=sys.stderr)

    # Query with fields does not work for Japanese titles!
    query_track = to_query('track', track)
    query_album = to_query('album', album)

    if artist is not None:
        query_artist = to_query('artist', artist)
    else:
        query_artist = ''

    raw_query = f'{track} {album} {artist}'
    query = f'{query_track} {query_album} {query_artist}'
    if len(query) > 80:
        query = f'{query_track} {query_album}'

    results = sp.search(query, limit=1, type="track", market='JP')
    if results['tracks']['total'] == 0:
        if raw_query != query:
            results = sp.search(query, limit=1, type="track", market='JP')

    if results['tracks']['total'] > 0:
        sp_track = results['tracks']['items'][0]
        sp_album = sp_track['album']
        artists = ' '.join(artist['name'] for artist in sp_track['artists'])
        id_ = sp_track['id']
        print(
            f"{colored('Found!', colorama.Fore.GREEN)} track: {track_term(sp_track['name'])} "
            f"album: {album_term(sp_album['name'])} artist: {artist_term(artists)}, ID: {id_}",
            file=sys.stderr
        )
        return id_
    else:
        print(f"{colored('Not found!', colorama.Fore.RED)}: {raw_query}", file=sys.stderr)


def search_album(title: str, artist: Optional[str]) -> Optional[str]:
    print(f"QUERY  name: {album_term(title)}, artist: {artist_term(artist or '')}", file=sys.stderr)

    # Query with fields does not work for Japanese titles!
    query_title = to_query('album', title)

    if artist is not None:
        query_artist = to_query('artist', artist)
    else:
        query_artist = ''

    query = f'{query_artist} {query_title}'

    results = sp.search(query, limit=1, type="album", market='JP')
    if results['albums']['total'] > 0:
        album = results['albums']['items'][0]
        artists = ' '.join(artist['name'] for artist in album['artists'])
        id_ = album['id']
        print(
            f"{colored('Found!', colorama.Fore.GREEN)} name: {album_term(album['name'])}, artist: {artist_term(artists)}, ID: {id_}",
            file=sys.stderr
        )
        return id_
    else:
        print(f"{colored('Not found!', colorama.Fore.RED)}", file=sys.stderr)


def tracks(json_file: os.PathLike):
    track_ids = []
    for track in json.load(open(json_file)):
        # Save only liked tracks
        if not track['liked']:
            continue
        time.sleep(1)
        if (track_id := search_track(track['track'], track['album'], track.get('artist'))) is not None:
            track_ids.append(track_id)
    print(json.dumps({'track_ids': track_ids}))


def albums(json_file: os.PathLike):
    album_ids = []
    for album in json.load(open(json_file)):
        time.sleep(1)
        if (album_id := search_album(album['album'], album.get('artist'))) is not None:
            album_ids.append(album_id)
    print(json.dumps({'album_ids': album_ids}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Search Spotify track/album IDs')
    parser.add_argument('-a', '--albums', dest='albums_json', type=str, help="Albums JSON file")
    parser.add_argument('-t', '--tracks', dest='tracks_json', type=str, help="Tracks JSON file")
    args = parser.parse_args()

    if args.albums_json is None and args.tracks_json is None:
        parser.print_help()
        sys.exit(1)

    colorama.init()
    if args.albums_json is not None:
        albums(args.albums_json)

    if args.tracks_json is not None:
        tracks(args.tracks_json)

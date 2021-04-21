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


def album_term(text: str):
    return colored(text, colorama.Fore.LIGHTMAGENTA_EX)


def artist_term(text: str):
    return colored(text, colorama.Fore.LIGHTBLUE_EX)


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
            f"{colored('Found!', colorama.Fore.GREEN)} name: {album_term(album['name'])}, artist: {artist_term(artists)}, ID: {id_} ",
            file=sys.stderr
        )
        return id_
    else:
        print(f"{colored('Not found!', colorama.Fore.RED)}", file=sys.stderr)


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
    args = parser.parse_args()

    if args.albums_json is None:
        parser.print_help()
        sys.exit(1)

    colorama.init()
    if args.albums_json is not None:
        albums(args.albums_json)

import argparse
import json
import os
import sys
import time

import spotipy
from spotipy.oauth2 import SpotifyOAuth

# https://developer.spotify.com/documentation/web-api/reference/#endpoint-save-albums-user
MAX_IDS_LENGTH = 50

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=["user-library-modify"]))


def albums(json_file: os.PathLike):
    album_ids = list(reversed(json.load(open(json_file))['album_ids']))
    for i in range(0, len(album_ids), MAX_IDS_LENGTH):
        time.sleep(2)
        sp.current_user_saved_albums_add(album_ids[i:i+MAX_IDS_LENGTH])


def tracks(json_file: os.PathLike):
    track_ids = list(reversed(json.load(open(json_file))['track_ids']))
    for i in range(0, len(track_ids), MAX_IDS_LENGTH):
        time.sleep(2)
        sp.current_user_saved_tracks_add(reversed(track_ids[i:i+MAX_IDS_LENGTH]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Save Spotify track/album IDs')
    parser.add_argument('-a', '--albums', dest='albums_json', type=str, help="Album IDs JSON file")
    parser.add_argument('-t', '--tracks', dest='tracks_json', type=str, help="Track IDs JSON file")
    args = parser.parse_args()

    if args.albums_json is None and args.tracks_json is None:
        parser.print_help()
        sys.exit(1)

    if args.albums_json is not None:
        albums(args.albums_json)

    if args.tracks_json is not None:
        tracks(args.tracks_json)

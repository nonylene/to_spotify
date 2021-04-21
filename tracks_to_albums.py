import argparse
import json
import os


def main(json_file: os.PathLike):
    albums = set()
    for track in json.load(open(json_file)):
        albums.add((track['album'], track.get('artist')))

    albums_json = [{'album': album, 'artist': artist} for album, artist in albums]
    print(json.dumps(albums_json, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert tracks to albums for save')
    parser.add_argument('-t', '--tracks', dest='tracks_json', type=str, required=True, help="Tracks JSON file")
    args = parser.parse_args()
    main(args.tracks_json)

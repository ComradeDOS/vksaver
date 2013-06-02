#!/bin/env python
from os import path, mkdir
import argparse
from struct import unpack
from urllib import urlopen

from fuzzywuzzy.fuzz import ratio

from lastfm import get_loved_tracks
from vk import get_api_instance
from mp3 import get_bitrate


parser = argparse.ArgumentParser('Download loved lastfm tracks from vk.com')
#parser.add_argument('--lastfm-user', dest='lastfm_user', required=True,
#    help='Username for LstFM')
parser.add_argument('--min-bitrate', dest='min_bitrate', required=False,
    help='Minimal bitrate for files', type=int, default=128000)
parser.add_argument('--out-dir', dest='out_dir', required=False,
    help='Minimal bitrate for files', default='music')


if __name__ == '__main__':
    args = parser.parse_args()
    if path.exists(args.out_dir):
        if not path.isdir(args.out_dir):
            raise RuntimeError('Output directory not a directory!')
    else:
        mkdir(args.out_dir)
    vk_api = get_api_instance()
    for loved_track in get_loved_tracks('ComradeDOS' or args.lastfm_user):
        artist = loved_track.track.artist.name
        title = loved_track.track.title
        query = '%s - %s' % (artist, title)
        filename = path.join(args.out_dir, '%s.mp3' % query)
        if path.exists(filename):
            continue
        '''
        duration = loved_track.track.get_duration() / 1000
        deviation = duration * 0.03
        min_duration = duration - deviation
        max_duration = duration + deviation
        '''
        result = vk_api.audio.search(q=query)[1:]
        candidates = ()
        for track in result:
            '''
            if duration and not (min_duration <= track['duration'] <= max_duration):
                print duration, track['duration']
                continue
            '''
            name = '%(artist)s - %(title)s' % track
            full_p = (query, name)
            artist_p = (artist, track['artist'])
            title_p = (title, track['title'])
            weight = ratio(*full_p) + ratio(*artist_p) + ratio(*title_p)
            if weight >= 250:
                candidates += (track['url'], )
        if not candidates:
            print 'Can\'t find appropriate candidates for "%s" track' % query
            continue
        best_candidate = {
            'bitrate': 0,
            'url': None,
        }
        for candidate in candidates:
            bitrate = get_bitrate(candidate)
            if bitrate < args.min_bitrate:
                continue
            if bitrate > best_candidate['bitrate']:
                best_candidate.update({
                    'bitrate': bitrate,
                    'url': candidate
                })
            if bitrate == 320000:
                break
        if best_candidate['url'] is None:
            print 'Can\'t find candidate with appropriate bitrate for "%s" track' % query
        else:
            src = urlopen(best_candidate['url'])
            dst = open(filename, 'wb')
            dst.write(src.read())
            dst.close()
            src.close()

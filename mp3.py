from struct import unpack
from urllib import urlopen
from StringIO import StringIO

from mutagen.mp3 import MPEGInfo


def get_tags_len(lst):
    return (lst[0] << 21) + (lst[1] << 14) + (lst[2] << 7) + lst[3] 

def get_bitrate(url):
    response = urlopen(url)
    buff = response.read(10)
    header = unpack('!3sBBBBBBB', buff)
    if header[0] == 'ID3':
        response.read(get_tags_len(header[-4:]) - 10)
        buff = response.read(32)
    else:
        buff += response.read(22)
    try:
        bitrate = MPEGInfo(StringIO(buff)).bitrate
    except Exception, exc:
        print exc
        try:
            bitrate = MPEGInfo(StringIO(buff+response.read(512-32))).bitrate
        except Exception, exc:
            print exc
            bitrate = 0
    response.close()
    return bitrate

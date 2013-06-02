from pylast import get_lastfm_network

import settings


def get_loved_tracks(username):
    lastfm_client = get_lastfm_network(settings.LASTFM_API_KEY)
    user = lastfm_client.get_user(username)
    return user.get_loved_tracks()

import webbrowser
from json import loads
from urllib import urlencode, urlopen
from multiprocessing import Process, Pipe

from vkontakte import API

import settings
from server import Server, RequestHandler


def build_auth_url(redirect_uri):
    return 'https://oauth.vk.com/authorize?%s' % urlencode({
        'client_id': settings.VK_APP_ID,
        'redirect_uri': redirect_uri,
        'scope': 'audio',
        'display': 'page',
        'response_type': 'code',
    })

def build_ac_url(redirect_uri, code):
    return 'https://oauth.vk.com/access_token?%s' % urlencode({
        'client_id': settings.VK_APP_ID,
        'client_secret': settings.VK_APP_SECRET,
        'code': code,
        'redirect_uri': redirect_uri,
    })

def get_token(url):
    return loads(urlopen(url).read())['access_token']

def get_redirect_uri(server_address):
    return 'http://%s:%s' % server_address

def get_server_address():
    return ('localhost', 8000)

def get_code(server_address, url):
    p_conn, c_conn = Pipe()
    server = Server(server_address, RequestHandler, pipe=c_conn)
    process = Process(target=lambda s: s.handle_request(), args=(server, ))
    process.start()
    webbrowser.open(url)
    process.join()
    return p_conn.recv()

def get_api_instance():
    server_address = get_server_address()
    redirect_uri = get_redirect_uri(server_address)
    code = get_code(server_address, build_auth_url(redirect_uri))
    token = get_token(build_ac_url(redirect_uri, code))
    return API(token=token)

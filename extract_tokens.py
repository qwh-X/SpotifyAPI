import time
import json
from json import JSONDecodeError
import re

from playwright.sync_api import Response, Page

from logger_config import get_logger
from spotify_session import SpotifySession

INTERVAL = 100

AUTH_TOKEN = 'Authorization'
CLIENT_TOKEN = 'Client-Token'

RE_LIKED_URI = r"{\"use\sstrict\";let\s\w=\"[\w\d]{22}\",\w=`spotify:playlist:\${\w}`,\w=\"([\w\d]{22})\",\w=`spotify:playlist:\${\w}`;"
# RE_CDN_URL = r"https://open\.spotifycdn\.com/cdn/build/web-player/.*?\..*?\.js"
RE_CDN_URL = r"https://open\.spotifycdn\.com/cdn/build/web-player/web-player\..*?\.js"

ALLOWED_URI_OPERATIONS = {'fetchplaylist', 'playlistpermissions', 'centralisedstateplayeroptions', 'fetchplaylistcontents'}

OPEN_URL = "https://open.spotify.com"
SAVED_TRACKS_URL = "https://open.spotify.com/collection/tracks"

logger = get_logger(__name__)

def _extract_saved_uri(response: Response, session: SpotifySession) -> None:
    request = response.request

    if session.saved_uri:
        return

    if '/pathfinder/v2/query' in request.url:
        if not request.post_data:
            return
        try:
            post_data = json.loads(request.post_data)
        except JSONDecodeError:
            logger.error(f"Invalid json in v2/query page; url: {request.url}; post data: {request.post_data}")
            return

        if uri := post_data.get('variables', {}).get('uri', ''):
            if post_data.get('operationName').lower() not in ALLOWED_URI_OPERATIONS:
                return
            session.saved_uri = uri
            logger.debug(f'saved uri set to {session.saved_uri} from {request.url}')
    if request.method == 'GET' and re.match(RE_CDN_URL, request.url):
        logger.debug(f'found cdn url: {request.url}')
        if match := re.search(RE_LIKED_URI, response.text()):
            session.saved_uri = match.group(1)
            logger.debug(f'saved uri set to: {session.saved_uri} from {request.url}')

def _extract_api_headers(response: Response, session: SpotifySession) -> None:
    if session.api_headers[AUTH_TOKEN] and session.api_headers[CLIENT_TOKEN]:
        return

    auth = client_token = None

    request = response.request
    headers = {k.lower(): v for k, v in request.headers.items()}

    auth = headers.get(AUTH_TOKEN.lower(), auth)
    client_token = headers.get(CLIENT_TOKEN.lower(), client_token)

    session.api_headers[AUTH_TOKEN] = auth
    session.api_headers[CLIENT_TOKEN] = client_token

    if auth and client_token:
        logger.debug(f'found api tokens at {request.url}')

def get_api_headers_preset() -> dict:
    with open('api_headers.json') as f:
        # placeholder: Authorization, Client-Token
        api_headers = json.load(f)
        logger.debug('api headers preset loaded')

    api_headers[AUTH_TOKEN] = None
    api_headers[CLIENT_TOKEN] = None
    return api_headers

def init_session(session: SpotifySession, timeout=10_000) -> None:
    session.api_headers = get_api_headers_preset()

    session.page.goto(SAVED_TRACKS_URL, wait_until='domcontentloaded')

    def on_response(response: Response) -> None:
        _extract_api_headers(response, session)
        _extract_saved_uri(response, session)

    session.page.on('response', on_response)

    deadline = time.monotonic() + timeout / 1000
    while not (session.api_headers[AUTH_TOKEN] and
               session.api_headers[CLIENT_TOKEN] and
               session.saved_uri
            ):
        if time.monotonic() >= deadline:
            raise TimeoutError("failed to obtain api headers")

        session.page.wait_for_timeout(INTERVAL)

    session.page.remove_listener("response", on_response)

def is_valid_headers(session: SpotifySession) -> bool:
    return session.api_headers[AUTH_TOKEN] and session.api_headers[CLIENT_TOKEN]

if __name__ == '__main__':
    from playwright.sync_api import sync_playwright
    from playwright_stealth import Stealth

    from spotify_session import SpotifySession

    with Stealth().use_sync(sync_playwright()) as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
                storage_state="auth_state.json",
                )
        page = context.new_page()

        session = SpotifySession(page)

        init_session(session)

        for k, v in session.api_headers.items():
            print(f'{k:<22}: {v}')
        print()
        print(f'{"Saved-URI":<22}: {session.saved_uri}')

        context.close()
        browser.close()
    
    # with open('uri-reqs.json', 'w') as f:
    #     json.dump(uri_reqs, f, indent=2)


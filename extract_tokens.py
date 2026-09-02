import time
import json
from json import JSONDecodeError
import re
from dataclasses import dataclass
from contextlib import contextmanager
from typing import Iterable, Callable

from playwright.sync_api import Response, Page

from logger_config import get_logger
from process_page import on_response

INTERVAL = 100

AUTH_TOKEN = 'Authorization'
CLIENT_TOKEN = 'Client-Token'

RE_LIKED_URI = r"{\"use\sstrict\";let\s\w=\"[\w\d]{22}\",\w=`spotify:playlist:\${\w}`,\w=\"([\w\d]{22})\",\w=`spotify:playlist:\${\w}`;"
RE_CDN_URL = r"https://open\.spotifycdn\.com/cdn/build/web-player/web-player\..*?\.js"

ALLOWED_URI_OPERATIONS = {'fetchplaylist', 'playlistpermissions', 'centralisedstateplayeroptions', 'fetchplaylistcontents'}

OPEN_URL = "https://open.spotify.com"
SAVED_TRACKS_URL = "https://open.spotify.com/collection/tracks"
# v2_url = "https://api-partner.spotify.com/pathfinder/v2/query"

logger = get_logger(__name__)

api_headers = None
saved_uri = None

uri_reqs = []

@dataclass
class _State:
    saved_uri: str | None = None
    api_headers: dict | None = None
state = _State()

@contextmanager
def _response_handlers(page: Page, *handlers: Callable[[Response], None]):
    for handler in handlers:
        page.on("response", handler)
    try:
        yield
    finally:
        for handler in handlers:
            page.remove_listener("response", handler)

def _extract_saved_uri(response: Response, state: _State) -> None:
    request = response.request

    if state.saved_uri:
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
            logger.debug(f'saved uri set to {state.saved_uri} from {request.url}')
            state.saved_uri = uri
    if request.method == 'GET' and re.match(RE_CDN_URL, request.url):
        logger.debug(f'found cdn url: {request.url}')
        if match := re.search(RE_LIKED_URI, response.text()):
            state.saved_uri = match.group(1)
            logger.debug(f'saved uri set to: {state.saved_uri} from {request.url}')

def _extract_auth(response: Response, state: _State) -> None:
    if state.api_headers[AUTH_TOKEN] and state.api_headers[CLIENT_TOKEN]:
        return

    auth = client_token = None

    request = response.request
    headers = {k.lower(): v for k, v in response.request.headers}

    auth = headers.get(AUTH_TOKEN.lower(), auth)
    client_token = headers.get(CLIENT_TOKEN.lower(), client_token)

    state.api_headers[AUTH_TOKEN] = auth
    state.api_headers[CLIENT_TOKEN] = client_token

    logger.debug(f'found api tokens at {request.url}')

def get_api_headers_preset() -> dict:
    with open('api_headers.json') as f:
        # placeholder: Authorization, Client-Token
        api_headers = json.load(f)
        logger.debug('api headers preset loaded')

    api_headers[AUTH_TOKEN] = None
    api_headers[CLIENT_TOKEN] = None
    return api_headers

def get_headers(page: Page, timeout=10_000):
    state = _State()

    state.api

    def handler(response):
        _extract_auth(response, state)

    with _response_handlers(page, handler):
        page.goto(SAVED_TRACKS_URL, wait_until='domcontentloaded')

        deadline = time.monotonic() + timeout / 1000

        while not (state.api_headers[AUTH_TOKEN] and state.api_headers[CLIENT_TOKEN]):
            if time.monotonic() >= deadline:
                raise TimeoutError("failed to obtain api headers")

            page.wait_for_timeout(INTERVAL)

    return state.api_headers

def get_saved_uri(page, timeout=10_000):
    state = _State()

    def handler(response):
        _extract_saved_uri(response, state)

    with _response_handlers(page, handler):
        page.goto(tracks_url)

        deadline = time.monotonic() + timeout / 1000

        while state.saved_uri is None:
            if time.monotonic() >= deadline:
                raise TimeoutError("Failed to obtain saved URI")

            page.wait_for_timeout(INTERVAL)

    return state.saved_uri

if __name__ == '__main__':
    from playwright.sync_api import sync_playwright
    from playwright_stealth import Stealth

    logger = get_logger(__name__)

    with Stealth().use_sync(sync_playwright()) as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
                storage_state="auth_state.json",
                )
        page = context.new_page()

        api_headers = get_headers(page)
        for k,v in api_headers.items():
            print(f'{k:<30}: {v}')

        saved_uri = get_saved_uri(page)
        print(f'{saved_uri=}')

        context.close()
        browser.close()
    
    # with open('uri-reqs.json', 'w') as f:
    #     json.dump(uri_reqs, f, indent=2)


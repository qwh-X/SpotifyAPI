import json
from typing import Iterable

from models import Playlist
from spotify_session import SpotifySession
from extract_tokens import is_valid_headers

PATHFINDER_URL = "https://api-partner.spotify.com/pathfinder/v2/query"


with open('fetch_playlists_post_data.json') as f:
    # placeholders: limit, offset
    fetch_playlists_post_data = json.load(f)

def fetch_playlists(session: SpotifySession, limit=50, offset=0) -> Iterable[Playlist]:
    assert is_valid_headers(session)
    fetch_playlists_post_data['variables']['limit'] = limit
    fetch_playlists_post_data['variables']['offset'] = offset

    response = session.page.request.post(
            PATHFINDER_URL,
            headers=session.api_headers,
            data = fetch_playlists_post_data
            )
    if response.status != 200:
        raise Exception(f'Returned code: {response.status}. {response.json()}')

    playlists = []

    saved_uri = session.saved_uri
    assert saved_uri

    data = response.json()

    # print(data)
    with open('playlist-fetch-res.json', 'w') as f:
        json.dump(data, f, indent=2)

    items = data['data']['me']['libraryV3']['items']

    for item in items:
        playlist = Playlist.from_api_json(item, saved_uri)
        playlists.append(playlist)

    return playlists

if __name__ == '__main__':
    from playwright.sync_api import sync_playwright
    from playwright_stealth import Stealth

    from extract_tokens import init_session

    with Stealth().use_sync(sync_playwright()) as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
                storage_state="auth_state.json",
                )
        page = context.new_page()

        session = SpotifySession(page)

        init_session(session)

        playlists = fetch_playlists(session, limit=200)

        for playlist in playlists:
            print(playlist)



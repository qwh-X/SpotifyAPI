import json

from logger_config import get_logger
from extract_tokens import is_valid_headers
from spotify_session import SpotifySession
from models import Song, Playlist

PATHFINDER_URL = "https://api-partner.spotify.com/pathfinder/v2/query"

logger = get_logger(__name__)

with open('fetch_songs_post_data.json') as f:
    # placeholders: limit, offset
    fetch_songs_post_data = json.load(f)

def fetch_songs(session: SpotifySession, playlist: Playlist, limit=50, offset=0):
    fetch_songs_post_data['variables']['limit'] = limit
    fetch_songs_post_data['variables']['offset'] = offset
    assert playlist.uri
    fetch_songs_post_data['variables']['uri'] = playlist.uri

    assert is_valid_headers(session)

    response = page.request.post(
            PATHFINDER_URL,
            headers=session.api_headers,
            data = fetch_songs_post_data
            )

    if response.status != 200:
        raise Exception(f'Returned code: {response.status}. {response.json()}')

    songs = []

    data = response.json()

    # with open('songs-fetch-res.json', 'w') as f:
    #     json.dump(data, f, indent=2)
    
    if data.get('data', {}).get('playlistV2', {}).get('content', {}).get('items', None) is None:
        with open('songs-fetch-res.json', 'w') as f:
            json.dump(data, f, indent=2)
        raise ValueError('Wrong root structure')

    items = data['data']['playlistV2']['content']['items']
    for item in items:
        try:
            data = item['itemV2']['data']
            song = Song.from_api_json(data)
            songs.append(song)
        except Exception as e:
            logger.error(repr(e))
            continue

    return songs

if __name__ == '__main__':
    from playwright.sync_api import sync_playwright
    from playwright_stealth import Stealth

    from extract_tokens import init_session
    from extract_playlists import fetch_playlists

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
            songs = fetch_songs(session, playlist)
            print(playlist)
            for i, song in enumerate(songs, start=1):
                print(f'  {i:03} {song}')
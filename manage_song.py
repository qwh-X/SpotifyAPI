import json
from typing import Literal, Iterable

import spotify_session
from json_util import access_by_path, set_by_path
from models import Playlist, Song
from spotify_session import SpotifySession
from extract_tokens import is_valid_headers

PATHFINDER_URL = "https://api-partner.spotify.com/pathfinder/v2/query"

# NOTE: apart from applyCurations, addToLibrary and removeFromLibrary exist.
# NOTE: the advantage of using applyCurations is being able to add/remove track[s] from any playlist[s]
# NOTE: as opposed to only your library

with open('curate_song_post_data.json') as f:
    # placeholders:
    # .variables.input
    #   .curations[
    #     .contextUri: PlaylistUri
    #     .curationType: UNCURATE | CURATE
    #     ]
    #   .itemUris: [TrackUri]
    curate_track_post_data = json.load(f)

def add_tracks_playlists(session: SpotifySession, playlists: list[Playlist], tracks: list[Song]):
    return _apply_curations(session, playlists, tracks, ["curate"] * len(playlists))

def add_tracks_playlist(session: SpotifySession, playlist: Playlist, tracks: list[Song]):
    return _apply_curations(session, [playlist], tracks, ["curate"])

def remove_tracks_from_playlists(session: SpotifySession, playlists: list[Playlist], tracks: list[Song]):
    return _apply_curations(session, playlists, tracks, ["uncurate"] * len(playlists))

def remove_tracks_from_playlist(session: SpotifySession, playlist: Playlist, tracks: list[Song]):
    return _apply_curations(session, [playlist], tracks, ["uncurate"])

def _mk_curations(playlists: list[Playlist], op_types: list[Literal['curate', 'uncurate']]):
    curations = []
    for playlist, op_type in zip(playlists, op_types):
        curations.append({
            'contextUri': playlist.uri,
            'curationType': op_type.upper(),
        })
    return curations

def _apply_curations(session: SpotifySession, playlists: list[Playlist], tracks: list[Song],
                     op_types: list[Literal['curate', 'uncurate']]) -> list[bool]:
    # TODO: add limits to how many tracks can be curated?
    assert is_valid_headers(session)

    assert len(playlists) == len(op_types)

    curations = _mk_curations(playlists, op_types)

    tracks_uris = [track.uri for track in tracks]
    set_by_path(curate_track_post_data, 'variables.input.curations', curations)
    set_by_path(curate_track_post_data, 'variables.input.itemUris', tracks_uris)

    # print(json.dumps(curate_track_post_data, indent=2))
    response = session.page.request.post(
        PATHFINDER_URL,
        headers=session.api_headers,
        data=curate_track_post_data
    )

    if response.status != 200:
        raise Exception(f'Returned code: {response.status}. {response.json()}')

    applied_curations = access_by_path(response.json(), 'data.applyCurations')

    # print(json.dumps(applied_curations, indent=2))

    is_curated = []

    for applied_curation in applied_curations:
        typename = applied_curation['__typename'].lower()
        if typename == 'trackresponsewrapper':
            is_curated.append(access_by_path(applied_curation, 'data.isCurated'))
        elif typename == 'genericerror':
            msg = applied_curation['message']
            raise Exception(f"Error: failed to apply curations: {msg}")

    return is_curated

if __name__ == '__main__':
    import random

    from playwright.sync_api import sync_playwright
    from playwright_stealth import Stealth

    from extract_tokens import init_session
    from extract_playlists import fetch_playlists
    from extract_songs import fetch_songs

    with Stealth().use_sync(sync_playwright()) as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            storage_state="auth_state.json",
        )
        page = context.new_page()

        session = SpotifySession(page)

        init_session(session)

        playlists = fetch_playlists(session, limit=200)
        if len(playlists) >= 2:
            p_from = random.choice(playlists)
            playlists.remove(p_from)
            p_to = random.choice(playlists)

            tracks = fetch_songs(session, p_from, limit=100)

            if len(tracks) >= 1:
                track = random.choice(tracks)

                print(f'moving track {track.name} from {p_from.name} to {p_to.name}')

                is_curated = remove_tracks_from_playlist(session, p_from, [track])[0]
                print(f'"{track.name}" in "{p_from.name}": {is_curated}')

                is_curated = add_tracks_playlist(session, p_to, [track])[0]
                print(f'"{track.name}" in "{p_to.name}": {is_curated}')
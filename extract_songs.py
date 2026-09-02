import json

class Date:
    def __init__(self, iso, precision):
        self.iso = iso
        self.precision = precision

    @classmethod
    def from_json(cls, data):
        # .data.playlistV2.content.items[].itemV2.data[...].date
        iso = data['isoString']
        precision = data['precision']
        return cls(iso, precision)

    def __repr__(self):
        return f'{self.iso}±{self.precision}'

class Album:
    def __init__(self, name, uri, artists, date):
        self.name = name
        self.uri = uri
        self.artists = artists
        self.date = date
        # coverArt

    @classmethod
    def from_json(cls, data):
        ".data.playlistV2.content.items[].itemV2.data.albumOfTrack"
        artists_items = data['artists']['items']
        artists = [Artist.from_json(artist) for artist in artists_items]
        name = data['name']
        uri = data['uri']
        date = Date.from_json(data['date'])
        return cls(name, uri, artists, date)

    def __repr__(self):
        return f'{self.name} - {self.artists} ({self.date}) @ {self.uri}'

class Artist:
    def __init__(self, name, uri):
        self.name = name
        self.uri = uri

    @classmethod
    def from_json(cls, data):
        ".data.playlistV2.content.items[].itemV2.data.artists.items[]"
        uri = data['uri']
        name = data['profile']['name']
        return cls(name, uri)

    def __repr__(self):
        return f'{self.name} @ {self.uri}'

class Song:
    def __init__(self, name, uri, duration, artists, album):
        self.name = name
        self.uri = uri
        self.duration = duration
        self.artists = artists
        self.album = album

    @classmethod
    def from_json(cls, data):
        ".data.playlistV2.content.items[].itemV2.data"
        assert data['__typename'].lower() == 'track'
        album = Album.from_json(data['albumOfTrack'])
        artists_items = data['artists']['items']
        artists = [Artist.from_json(artist) for artist in artists_items]
        duration = data['trackDuration']['totalMilliseconds']
        uri = data['uri']
        name = data['name']
        return cls(name, uri, duration, artists, album)

    def __repr__(self):
        artists_names = [artist.name for artist in self.artists]
        if len(artists_names) > 1:
            artists = ', '.join(artists_names)
            artists = '(' + artists + ')'
        else:
            artists = artists_names[0]
        mins, secs = divmod(self.duration, (60*1000))
        secs, ms = divmod(secs, 1000)
        return f'{self.name} - {artists} ({mins}:{secs:02}.{ms:03}) @ {self.uri}'

v2_url = "https://api-partner.spotify.com/pathfinder/v2/query"

with open('fetch_songs_post_data.json') as f:
    # placeholders: limit, offset
    fetch_songs_post_data = json.load(f)

def fetch_songs(api_headers, page, playlist, limit=50, offset=0, verbose=False):
    fetch_songs_post_data['variables']['limit'] = limit
    fetch_songs_post_data['variables']['offset'] = offset
    fetch_songs_post_data['variables']['uri'] = playlist['uri'] if isinstance(playlist, dict) else playlist

    response = page.request.post(
            v2_url,
            headers=api_headers,
            data = fetch_songs_post_data
            )
    if response.status != 200:
        raise Exception(f'Returned code: {response.status}. {response.json()}')

    songs = []

    data = response.json()

    with open('songs-fetch-res.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    if data.get('data', {}).get('playlistV2', {}).get('content', {}).get('items', None) is None:
        with open('songs-fetch-res.json', 'w') as f:
            json.dump(data, f, indent=2)
        raise ValueError('Wrong root structure')

    items = data['data']['playlistV2']['content']['items']
    for item in items:
        try:
            data = item['itemV2']['data']
            song = Song.from_json(data)
            songs.append(song)
        except Exception as e:
            if verbose:
                print(f'Exception while parsing song: {e}')
            continue

    return songs

if __name__ == '__main__':
    import time

    from playwright.sync_api import sync_playwright
    from playwright_stealth import Stealth

    from extract_tokens import get_headers
    from extract_playlists import fetch_playlists

    with Stealth().use_sync(sync_playwright()) as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
                storage_state="auth_state.json",
                )
        page = context.new_page()

        api_headers = get_headers(page, verbose=0)
        playlists = fetch_playlists(api_headers, page, limit=200)

        for playlist in playlists[1:2]:
            songs = fetch_songs(api_headers, page, playlist, limit=500)
            for i, song in enumerate(songs, start=1):
                print(song)

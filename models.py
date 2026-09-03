PSEUDO_LIKED_URI = "spotify:collection:tracks"

class Date:
    def __init__(self, iso, precision):
        self.iso = iso
        self.precision = precision

    @classmethod
    def from_api_json(cls, data):
        ".data.playlistV2.content.items[].itemV2.data[...].date"
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
    def from_api_json(cls, data):
        ".data.playlistV2.content.items[].itemV2.data.albumOfTrack"
        artists_items = data['artists']['items']
        artists = [Artist.from_api_json(artist) for artist in artists_items]
        name = data['name']
        uri = data['uri']
        date = Date.from_api_json(data['date'])
        return cls(name, uri, artists, date)

    def __repr__(self):
        return f'{self.name} - {self.artists} ({self.date}) @ {self.uri}'

class Playlist:
    def __init__(self,
                 name,
                 uri,
                 count=0,
                 added_at=None,
                 played_at=None,
                 pinnable=True,
                 pinned=False,
                 typename=None,
                 current_user_capabilities=None,
                 description=None,
                 format_=None,
                 attributes=None,
                 songs=None):
        self.name = name
        self.uri = uri
        self.count = count
        self.added_at = added_at
        self.played_at = played_at
        self.pinnable = pinnable
        self.pinned = pinned
        self.typename = typename
        self.current_user_capabilities = current_user_capabilities
        self.description = description
        self.format_ = format_
        self.attributes = attributes # ?
        self.songs = songs
        # what is depth
        # image?

    def set_songs(self, songs):
        self.songs = songs

    def get_songs(self):
        if self.songs is None:
            raise ValueError("No songs set.")
        return self.songs

    @classmethod
    def from_api_json(cls, data, saved_uri):
        ".data.me.libraryV3.items[*]"
        added_at = (data.get('addedAt') or {}).get('isoString', None)
        pinnable = data['pinnable']
        pinned = data['pinned']
        played_at = (data.get('playedAt') or {}).get('isoString', None)

        item = data['item']

        item_data = item['data']
        typename = item_data['__typename']
        description = item_data.get('description')
        format_ = item_data.get('format')
        name = item_data['name']
        uri = item_data['uri'] if item_data['uri'] != PSEUDO_LIKED_URI else saved_uri
        count = item_data.get('count', None) # only spotify:collection:tracks implements it
        current_user_capabilities = item_data.get('currentUserCapabilities')

        attributes = item_data.get('attributes', {}) # not implemented by spotify::collection:tracks

        return cls(name, uri, count, added_at, played_at,
                   pinnable, pinned, typename, current_user_capabilities, description,
                   format_, attributes)

    def __repr__(self) -> str:
        return f'{self.name:<30} {self.uri}'

class Artist:
    def __init__(self, name, uri):
        self.name = name
        self.uri = uri

    @classmethod
    def from_api_json(cls, data):
        ".data.playlistV2.content.items[].itemV2.data.artists.items[]"
        uri = data['uri']
        name = data['profile']['name']
        return cls(name, uri)

    def __repr__(self):
        return f'{self.name:<30} {self.uri}'

class Song:
    def __init__(self, name, uri, duration, artists, album):
        self.name = name
        self.uri = uri
        self.duration = duration
        self.artists = artists
        self.album = album

    @classmethod
    def from_api_json(cls, data):
        ".data.playlistV2.content.items[].itemV2.data"
        assert data['__typename'].lower() == 'track', f"\"{data['__typename'].lower()}\" is not a track"
        album = Album.from_api_json(data['albumOfTrack'])
        artists_items = data['artists']['items']
        artists = [Artist.from_api_json(artist) for artist in artists_items]
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
        return f'{self.name:<30} {artists:<30} ({mins}:{secs:02}.{ms:03}) @ {self.uri}'
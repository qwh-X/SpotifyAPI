## dev

TODO: add support for adding songs i guess
NOTE: could be using `fetchPlaylistContents` instead of `fetchPlaylist`

## files

### extract_tokens

provides init session and auth header validation(kinda)

### extract_playlists

extracts playlists from a session
- params: limit, offset

### extract_songs

extract songs from a playlist ( episodes are not supported )
- params: playlist: .uri, limit, offset
- add passing playlist by uri?

### models

contains class definitions for Album Song Artist Playlist[...]
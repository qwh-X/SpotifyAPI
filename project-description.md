## dev

currently refactoring extract_tokens for modularity

## files

### extract_tokens

use the api to extract auth and client token
those are necessary for making any further requests

- refactor: make headers a struct/class?

### extract_playlists

extract playlists.

### extract_songs

- defines Album Song Artist

extract songs from a playlist ( episodes are not supported )

- refactor: add fields to classes?
- move classes out
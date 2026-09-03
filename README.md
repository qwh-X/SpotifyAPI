_Since spotify has made its official api premium only, I am trying to replace parts of it_

## API

The program uses [playwright](https://github.com/microsoft/playwright) to open spotify in a web browser ( headless[ie invisible to you] or not )
The requests made by your browser are then intercepted and manipulated in our own interests:
- to get your saved songs
- saved playlists
- songs in playlists
- add songs to library/playlist 
- follow artist
- ...

This approach is far from the official api.

It is not maintained by spotify developers in any way, meaning any update spotify receives could break this project.
This also implies that you could be flagged as a bot, which can carry further consequences for your account

Some parts of the code rely solely on the probability that the browser triggers a request to an endpoint

## Usage examples
Almost every script has includes showcase/test code in `if __name__ == '__main__': ...` blocks.

[Songs extraction from playlists](/extract_songs.py)

## Logging in
Run [login.py](/login.py). A browser with the login page will pop up. Once you've logged in, press enter in the console.
The state of your browser will be saved into `auth_state.json`.
Your password doesn't get saved. Only the tokens. You will have to sign in again, once the tokens expire.

## Prerequisites

- Python installed
- Python Playwright installed ( with a browser )
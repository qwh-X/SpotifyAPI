import json

from extract_tokens import get_liked_uri

v2_url = "https://api-partner.spotify.com/pathfinder/v2/query"
pseudo_liked_uri = "spotify:collection:tracks"

with open('fetch_playlists_post_data.json') as f:
    # placeholders: limit, offset
    fetch_playlists_post_data = json.load(f)

def fetch_playlists(api_headers, page, limit=50, offset=0):
    fetch_playlists_post_data['variables']['limit'] = limit
    fetch_playlists_post_data['variables']['offset'] = offset
    response = page.request.post(
            v2_url,
            headers=api_headers,
            data = fetch_playlists_post_data
            )
    if response.status != 200:
        raise Exception(f'Returned code: {response.status}. {response.json()}')

    playlists = []

    liked_uri = get_liked_uri(page)
    assert liked_uri is not None

    data = response.json()

    # print(data)
    # with open('playlist-fetch-res.json', 'w') as f:
    #     json.dump(data, f, indent=2)

    items = data['data']['me']['libraryV3']['items']

    for item in items:
        data = item['item']['data']
        uri = data['uri'] if data['uri'] != pseudo_liked_uri else liked_uri
        length = data.get('count')
        name = data['name']

        playlists.append({
            'uri': uri,
            'length': length,
            'name': name,
            })

    return playlists

if __name__ == '__main__':
    from playwright.sync_api import sync_playwright

    from playwright_stealth import Stealth
    from extract_tokens import get_headers

    with Stealth().use_sync(sync_playwright()) as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
                storage_state="auth_state.json",
                )
        page = context.new_page()

        api_headers = get_headers(page)
        playlists = fetch_playlists(api_headers, page, limit=200)

        for playlist in playlists:
            print(f"{playlist['name']:<30} {playlist['uri']:<42} {playlist['length']}")



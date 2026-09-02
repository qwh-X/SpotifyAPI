import time
import json
from playwright.sync_api import sync_playwright

open_url = "https://open.spotify.com"
v2_url = "https://api-partner.spotify.com/pathfinder/v2/query"

with open('fetch_playlists_post_data.json') as f:
    # placeholders: limit, offset
    fetch_playlists_post_data = json.load(f)
    fetch_playlists_post_data["variables"]["limit"] = 2500
    fetch_playlists_post_data["variables"]["offset"] = 0

with open('api_headers.json') as f:
    # placeholder: authorization, client-token
    # MUST ADD
    api_headers = json.load(f)

elements = [
    '[data-testid="control-button-playpause"]',
    '[data-testid="control-button-repeat"]',
    '[data-testid="home-button"]',
    '[data-testid="search-input"]'
]

urls = []

def is_valid_json(string):
    try:
        json.loads(string)
        return True
    except:
        return False

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
                storage_state="auth_state.json",
                # locale='en-US',
                # extra_http_headers={
                #     'Accept-Language': 'en-US,en,q=0.9'
                #     },
                )
    page = context.new_page()

    responses = []

    auth = client_token = None
    
    def on_request(request):
        pass
    
    def on_response(response):
        global auth, client_token
        request = response.request
        print(request.url, 'authorization' in request.headers)
        if 'authorization' in request.headers\
                and 'client-token' in request.headers:
                auth = request.headers.get('authorization')
                client_token = request.headers.get('client-token')
        if '/pathfinder/v2/query' in response.url:
            responses.append({
                'post_data': json.loads(request.post_data),
                'url': response.url,
                'req_headers': dict(request.headers),
                'json': response.json(),
                })
    
    page.on("request", on_request)
    page.on("response", on_response)

    page.goto(open_url)

    while not (auth and client_token):
        time.sleep(0.1)

    api_headers['authorization'] = auth
    api_headers['client-token'] = client_token

    response = page.request.post(
            v2_url,
            headers=api_headers,
            data = fetch_playlists_post_data
            )

    print(response.status)

    with open('playlist-fetch-res.json', 'w') as f:
        json.dump(response.json(), f, indent=2)

    input("Press enter to close: ")

    # s = time.time()
    # for i, selector in enumerate(elements, start=1):
    #     page.wait_for_selector(selector, state='visible', timeout=30000)
    #     print(f'{selector} {i}/{len(elements)} loaded at {(time.time()-s)*1000:.2f}ms')
    #
    # page.wait_for_load_state('networkidle')
    # page.wait_for_timeout(10000)

    with open('responses.json', 'w') as f:
        json.dump(responses, f, indent=2)

    # with open('urls.txt', 'w') as f:
    #     f.write('\n'.join(urls))

    context.close()
    browser.close()

    # res = traffic_data['responses'][0]
    # for k,v in res.items():
    #     print(f'{k}: {type(v)}')

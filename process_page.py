import time
# import gzip
# import brotli
import json
from re import L
from playwright.sync_api import sync_playwright

open_url = "https://open.spotify.com"
tracks_url = "https://open.spotify.com/collection/tracks"

elements = [
    '[data-testid="control-button-playpause"]',
    '[data-testid="control-button-repeat"]',
    '[data-testid="home-button"]',
    '[data-testid="search-input"]'
]

def is_valid_json(string):
    try:
        json.loads(string)
        return True
    except:
        return False

# def decode_content(body_bytes, encoding):
#     try:
#         if encoding == 'gzip':
#             return gzip.decompress(body_bytes)
#         elif encoding == 'br':
#             return brotli.decompress(body_bytes)
#         else:
#             # raise ValueError(f'Unknown encoding: {encoding}')
#             return body_bytes
#     except Exception as e:
#         print(f'Failed decompressing {body_bytes[:50]} with {encoding}: {e}')

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
                storage_state="auth_state.json",
                locale='en-US',
                extra_http_headers={
                    'Accept-Language': 'en-US,en,q=0.9'
                    },
                )
    page = context.new_page()

    traffic_data = {
        'requests': [],
        'responses': [],
        'errors': []
    }
    
    def on_request(request):
        return
        traffic_data['requests'].append({
            'url': request.url,
            'method': request.method,
            'headers': dict(request.headers),
            'post_data': request.post_data,
            # 'timing': request.timing
        })
    
    def on_response(response):
        request = response.request
        try:
            body = response.text()
        except:
            # print(f'Failed decoding from url: {response.url}')
            # print(response.headers.get('content-type')) // fonts
            return
        is_json = is_valid_json(body)
        if request.post_data is not None:
            req_post_data = request.post_data.replace('\n', ',')
        else:
            req_post_data = 'null'
        try:
            if req_post_data is not None:
                json.loads(req_post_data)
        except Exception as e:
            print(req_post_data)
            return
            # print(e)
        data = {
            'url': response.url,
            'status': response.status,
            # 'status_text': response.status_text,
            'headers': dict(response.headers),
            'request-headers': dict(request.headers),
            'request-post_data': json.loads(req_post_data) if req_post_data else None,
            # 'server_addr': response.server_addr(),
            # 'finished': response.finished(),
            # 'ok': response.ok,
            # 'frame': response.frame // not serializable
        }
        if is_json:
            data['json'] = json.loads(body)
        else:
            data['body'] = body
        traffic_data['responses'].append(data)
    
    def on_request_failed(request):
        traffic_data['errors'].append({
            'url': request.url,
            'error': request.failure.error_text if request.failure else 'Unknown error'
        })
    
    # Register all event listeners
    # page.on("request", on_request)
    page.on("response", on_response)
    # page.on("requestfailed", on_request_failed)

    page.goto(tracks_url)

    # input("Press enter to close: ")

    # print(traffic_data)

    with open('traffic_data.json', 'w') as f:
        json.dump(traffic_data, f, indent=2)
    s = time.time()
    # for i, selector in enumerate(elements, start=1):
    #     page.wait_for_selector(selector, state='visible', timeout=30000)
    #     print(f'{selector} {i}/{len(elements)} loaded at {(time.time()-s)*1000:.2f}ms')

    page.wait_for_load_state('networkidle')
    page.wait_for_timeout(1000)

    # with open('open-page.html', 'w') as f:
    #     f.write(page.content())

    context.close()
    browser.close()

    # res = traffic_data['responses'][0]
    # for k,v in res.items():
    #     print(f'{k}: {type(v)}')

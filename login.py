import time
import random
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

def run():
    with Stealth().use_sync(sync_playwright()) as p:
    # with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        context = browser.new_context(
                # locale='en-US',
                # extra_http_headers={
                #     'Accept-Language': 'en-US,en,q=0.9'
                #     },
                )
        page = context.new_page()

        page.goto("https://accounts.spotify.com/en/login")
        
        # page.get_by_test_id("login-username").click()
        # time.sleep(random.random())
        # page.get_by_test_id("login-username").fill(email)
        # for c in email:
        #     page.keyboard.type(c)
        #     time.sleep(random.random())
        # page.get_by_test_id("login-button").click()
        # time.sleep(random.random())

        # code = input(f'code for {email}: ')
        # for c in code:
        #     page.keyboard.type(c)
        #     time.sleep(1)

        # page.goto("https://bot.sannysoft.com")
        input('Press enter after auth: ')

        context.storage_state(path="auth_state.json")
        # time.sleep(10)
        
        browser.close()

if __name__ == "__main__":
    run()

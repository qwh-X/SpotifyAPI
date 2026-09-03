import time
import random
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

def run():
    with Stealth().use_sync(sync_playwright()) as p:
        browser = p.firefox.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://accounts.spotify.com/en/login")
        input('Press enter after auth: ')

        context.storage_state(path="auth_state.json")
        
        browser.close()

if __name__ == "__main__":
    run()

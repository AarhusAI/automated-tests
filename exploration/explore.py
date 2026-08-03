"""
Exploration helper for writing Selenium tests.
Usage: python explore.py <url_path> [--login builder|user] [--click <selector> ...]

Navigates to TEST_DOMAIN+url_path, optionally logs in first, optionally
clicks elements (e.g. to open a menu or flip a toggle), then saves a
screenshot and page source for inspection.
"""

import os
import time
import argparse

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import dotenv

dotenv.load_dotenv()

CREDENTIALS = {
    "builder": ("BUILDER_USERNAME", "BUILDER_PASSWORD"),
    "user":    ("USER_USERNAME",    "USER_PASSWORD")
}

_HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT_SCREENSHOT = os.path.join(_HERE, "explore_screenshot.png")
OUTPUT_HTML       = os.path.join(_HERE, "explore_page.html")


def make_browser():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    browser = Chrome(options=options)
    browser.implicitly_wait(5)
    return browser


def login(browser, role):
    domain = os.environ["TEST_DOMAIN"]
    u_key, p_key = CREDENTIALS[role]
    browser.get(domain)
    browser.find_element(value="email").send_keys(os.environ[u_key])
    browser.find_element(value="password").send_keys(os.environ[p_key])
    browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    WebDriverWait(browser, 10).until(EC.url_to_be(domain))


def wait_for_page(browser):
    WebDriverWait(browser, 30).until(
        EC.invisibility_of_element_located((By.ID, "splash-screen"))
    )


def click(browser, selector):
    by = By.XPATH if selector.startswith(("//", "(")) else By.CSS_SELECTOR
    element = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((by, selector)))
    element.click()
    time.sleep(1)  # let menus/animations settle before the capture


def save_outputs(browser):
    browser.save_screenshot(OUTPUT_SCREENSHOT)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(browser.page_source)
    print(f"Screenshot : {OUTPUT_SCREENSHOT}")
    print(f"Page source: {OUTPUT_HTML}")
    print(f"Current URL: {browser.current_url}")
    print(f"Page title : {browser.title}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default="", help="URL path to append to TEST_DOMAIN")
    parser.add_argument("--login", choices=CREDENTIALS.keys(), help="Log in as this role first")
    parser.add_argument(
        "--click",
        action="append",
        default=[],
        metavar="SELECTOR",
        help="Click this element after the page loads, before capturing "
             "(CSS selector, or XPath if it starts with //; repeatable, clicked in order)",
    )
    args = parser.parse_args()

    domain = os.environ["TEST_DOMAIN"].rstrip("/")
    target = f"{domain}/{args.path.lstrip('/')}" if args.path else domain

    browser = make_browser()
    try:
        if args.login:
            login(browser, args.login)
        browser.get(target)
        wait_for_page(browser)
        for selector in args.click:
            click(browser, selector)
        save_outputs(browser)
    finally:
        browser.quit()


if __name__ == "__main__":
    main()

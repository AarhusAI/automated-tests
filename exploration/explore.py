"""
Exploration helper for writing Playwright tests.
Usage: python explore.py <url_path> [--login admin|builder|user] [--click <selector> ...]

Navigates to TEST_DOMAIN+url_path, optionally logs in first, optionally
clicks elements (e.g. to open a menu or flip a toggle), then saves a
screenshot and page source for inspection.
"""

import os
import sys
import time
import argparse

from playwright.sync_api import sync_playwright
import dotenv

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))  # make `tests` importable when run as a script
from tests import helpers  # noqa: E402

dotenv.load_dotenv()

CREDENTIALS = {
    "admin":   ("ADMIN_USERNAME",   "ADMIN_PASSWORD"),
    "builder": ("BUILDER_USERNAME", "BUILDER_PASSWORD"),
    "user":    ("USER_USERNAME",    "USER_PASSWORD")
}

OUTPUT_SCREENSHOT = os.path.join(_HERE, "explore_screenshot.png")
OUTPUT_HTML       = os.path.join(_HERE, "explore_page.html")


def click(page, selector):
    # Playwright detects XPath only for "//" and "..", so "(" needs an explicit prefix.
    if selector.startswith("("):
        selector = "xpath=" + selector
    page.locator(selector).first.click(timeout=10_000)
    time.sleep(1)  # let menus/animations settle before the capture


def save_outputs(page):
    page.screenshot(path=OUTPUT_SCREENSHOT)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(page.content())
    print(f"Screenshot : {OUTPUT_SCREENSHOT}")
    print(f"Page source: {OUTPUT_HTML}")
    print(f"Current URL: {page.url}")
    print(f"Page title : {page.title()}")


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
             "(CSS selector, or XPath if it starts with // or (; repeatable, clicked in order)",
    )
    args = parser.parse_args()

    domain = os.environ["TEST_DOMAIN"].rstrip("/")
    target = f"{domain}/{args.path.lstrip('/')}" if args.path else domain

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        if args.login:
            u_key, p_key = CREDENTIALS[args.login]
            helpers.login(page, os.environ[u_key], os.environ[p_key])
        page.goto(target)
        helpers.wait_for_app(page)
        for selector in args.click:
            click(page, selector)
        save_outputs(page)


if __name__ == "__main__":
    main()

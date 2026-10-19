import os

from playwright.sync_api import expect


def test_was_redirects_to_accessibility_statement(page):
    page.goto(os.environ["TEST_DOMAIN"] + "was")

    assert page.url.startswith("https://was.digst.dk/")
    expect(page.locator("h1")).to_have_text("Tilgængelighedserklæring")

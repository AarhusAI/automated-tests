import os

from playwright.sync_api import expect

from tests import helpers


def test_login_as_builder(page):
    helpers.open_chat(page, os.environ["BUILDER_USERNAME"], os.environ["BUILDER_PASSWORD"])

    assert page.url == os.environ["TEST_DOMAIN"] + "?model=aarhusai-start"
    expect(page.locator("#chat-input-container")).to_be_visible(timeout=10_000)

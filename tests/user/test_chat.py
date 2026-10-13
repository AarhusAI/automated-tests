import os

from playwright.sync_api import expect

from tests import helpers


def test_user_can_send_prompt_and_receive_response(page):
    helpers.open_chat(page, os.environ["USER_USERNAME"], os.environ["USER_PASSWORD"])

    expect(page.locator("#chat-input-container")).to_be_visible(timeout=10_000)

    response = helpers.send_prompt(page, "Say only the word: hello")
    assert response.strip()

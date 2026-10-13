import os

from tests import helpers


def test_user_can_read_response_aloud(page):
    helpers.open_chat(page, os.environ["USER_USERNAME"], os.environ["USER_PASSWORD"])

    helpers.send_prompt(page, "Say only the word: hello")

    # The deployment synthesises speech server-side; headless Chrome has no audio output to observe,
    # so assert the speech request succeeded.
    with page.expect_response(
        lambda r: r.url.endswith("/api/v1/audio/speech") and r.status == 200, timeout=30_000
    ):
        page.locator('button[id^="speak-button-"]').first.click()

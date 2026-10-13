import os
import time

import pytest
from playwright.sync_api import expect

from tests import helpers

FIXTURE_AUDIO = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "fixtures", "dictation_sample.wav")
)


@pytest.fixture
def page(browser_type, browser_type_launch_args, browser_context_args):
    # Fake-media flags are launch args, so this test needs its own browser.
    browser = browser_type.launch(**{
        **browser_type_launch_args,
        "args": [
            "--use-fake-ui-for-media-stream",
            "--use-fake-device-for-media-stream",
            f"--use-file-for-fake-audio-capture={FIXTURE_AUDIO}",
        ],
    })
    context = browser.new_context(**browser_context_args)
    yield context.new_page()
    context.close()
    browser.close()


def test_user_can_dictate_into_chat_input(page):
    helpers.open_chat(page, os.environ["USER_USERNAME"], os.environ["USER_PASSWORD"])

    expect(page.locator("#chat-input-container")).to_be_visible(timeout=10_000)

    page.locator("#voice-input-button").click()

    confirm = page.locator("#confirm-recording-button")
    confirm.wait_for(timeout=5_000)
    time.sleep(4)  # let the fake mic play the fixture WAV
    confirm.click()

    expect(page.locator("#chat-input")).to_contain_text("Hej med dig", timeout=30_000)

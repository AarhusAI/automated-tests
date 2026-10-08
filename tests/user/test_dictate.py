import os
import time
import unittest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import dotenv

from tests import helpers

dotenv.load_dotenv()

FIXTURE_AUDIO = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "fixtures", "dictation_sample.wav")
)


class TestUserDictate(helpers.BrowserTestCase):
    # Not headless: the fake mic needs a display (Xvfb in Docker).
    chrome_args = (
        "--use-fake-ui-for-media-stream",
        "--use-fake-device-for-media-stream",
        f"--use-file-for-fake-audio-capture={FIXTURE_AUDIO}",
    )

    def test_user_can_dictate_into_chat_input(self):
        browser = self.browser
        helpers.open_chat(browser, os.environ["USER_USERNAME"], os.environ["USER_PASSWORD"])

        WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, "chat-input-container")))

        browser.find_element(By.ID, "voice-input-button").click()

        confirm = WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable((By.ID, "confirm-recording-button"))
        )
        time.sleep(4)  # let the fake mic play the fixture WAV
        confirm.click()

        transcribed = WebDriverWait(browser, 30).until(
            lambda d: d.find_element(By.ID, "chat-input").text.strip()
        )
        self.assertIn("Hej med dig", transcribed)


if __name__ == "__main__":
    unittest.main()

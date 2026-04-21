import os
import time
import unittest

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import dotenv

from tests import helpers

dotenv.load_dotenv()

FIXTURE_AUDIO = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "fixtures", "dictation_sample.wav")
)


class TestUserDictate(unittest.TestCase):
    def setUp(self):
        options = Options()
        # options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--use-fake-ui-for-media-stream")
        options.add_argument("--use-fake-device-for-media-stream")
        options.add_argument(f"--use-file-for-fake-audio-capture={FIXTURE_AUDIO}")
        self.browser = Chrome(options=options)
        self.browser.implicitly_wait(5)

    def tearDown(self):
        self.browser.quit()

    def test_user_can_dictate_into_chat_input(self):
        browser = self.browser

        helpers.login(browser, os.environ["USER_USERNAME"], os.environ["USER_PASSWORD"])
        helpers.wait_for_app(browser)

        browser.find_element(By.ID, "voice-input-button").click()

        confirm = WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable((By.ID, "confirm-recording-button"))
        )
        time.sleep(4)  # let the fake mic play the fixture WAV
        confirm.click()

        WebDriverWait(browser, 30).until(
            lambda d: d.find_element(By.ID, "chat-input").text.strip() != ""
        )

        transcribed = browser.find_element(By.ID, "chat-input").text.strip()
        self.assertIn("Hej med dig", transcribed)


if __name__ == "__main__":
    unittest.main()

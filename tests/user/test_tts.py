import os
import unittest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import dotenv

from tests import helpers

dotenv.load_dotenv()


class TestUserTts(helpers.BrowserTestCase):
    def test_user_can_read_response_aloud(self):
        browser = self.browser
        helpers.open_chat(browser, os.environ["USER_USERNAME"], os.environ["USER_PASSWORD"])

        helpers.send_prompt(browser, "Say only the word: hello")
        browser.find_element(By.CSS_SELECTOR, 'button[id^="speak-button-"]').click()

        # The deployment synthesises speech server-side; headless Chrome has no audio output to observe,
        # so assert the speech request succeeded.
        WebDriverWait(browser, 30).until(lambda d: d.execute_script(
            "return performance.getEntriesByType('resource')"
            "    .some(e => e.name.endsWith('/api/v1/audio/speech') && e.responseStatus === 200);"
        ))


if __name__ == "__main__":
    unittest.main()

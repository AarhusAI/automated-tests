import os
import unittest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import dotenv

from tests import helpers

dotenv.load_dotenv()


class TestUserChat(helpers.BrowserTestCase):
    def test_user_can_send_prompt_and_receive_response(self):
        browser = self.browser
        helpers.open_chat(browser, os.environ["USER_USERNAME"], os.environ["USER_PASSWORD"])

        WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, "chat-input-container")))

        response = helpers.send_prompt(browser, "Say only the word: hello")
        self.assertTrue(response.strip())


if __name__ == "__main__":
    unittest.main()

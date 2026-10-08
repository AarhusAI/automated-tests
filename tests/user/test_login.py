import os
import unittest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import dotenv

from tests import helpers

dotenv.load_dotenv()


class TestUserLogin(helpers.BrowserTestCase):
    def test_login_as_user(self):
        browser = self.browser
        helpers.open_chat(browser, os.environ["USER_USERNAME"], os.environ["USER_PASSWORD"])

        self.assertEqual(browser.current_url, os.environ["TEST_DOMAIN"] + "?model=aarhusai-start")
        WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, "chat-input-container")))


if __name__ == "__main__":
    unittest.main()

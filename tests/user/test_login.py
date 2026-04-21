import os
import unittest

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import dotenv

from tests import helpers

dotenv.load_dotenv()


class TestUserLogin(unittest.TestCase):
    def setUp(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        self.browser = Chrome(options=options)
        self.browser.implicitly_wait(5)

    def tearDown(self):
        self.browser.quit()

    def test_login_as_user(self):
        helpers.login(self.browser, os.environ["USER_USERNAME"], os.environ["USER_PASSWORD"])

        self.assertEqual(self.browser.current_url, os.environ["TEST_DOMAIN"])


if __name__ == '__main__':
    unittest.main()

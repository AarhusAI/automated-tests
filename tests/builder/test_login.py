import os
import unittest

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import dotenv

from tests import helpers

dotenv.load_dotenv()


class TestBuilderLogin(unittest.TestCase):
    def setUp(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        self.browser = Chrome(options=options)
        self.browser.implicitly_wait(5)

    def tearDown(self):
        helpers.save_screenshot(self, self.browser)
        self.browser.quit()

    def test_login_as_builder(self):
        helpers.login(self.browser, os.environ["BUILDER_USERNAME"], os.environ["BUILDER_PASSWORD"])
        helpers.wait_for_app(self.browser)

        self.assertEqual(self.browser.current_url, os.environ["TEST_DOMAIN"])
        WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((By.ID, "chat-input-container")))


if __name__ == '__main__':
    unittest.main()

import os
import unittest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import dotenv

from tests import helpers

dotenv.load_dotenv()


@unittest.skipUnless(os.environ.get("ADMIN_USERNAME"), "ADMIN_USERNAME/ADMIN_PASSWORD not set")
class TestAdminLogin(helpers.BrowserTestCase):
    def test_login_as_admin(self):
        browser = self.browser
        helpers.open_chat(browser, os.environ["ADMIN_USERNAME"], os.environ["ADMIN_PASSWORD"])

        self.assertEqual(browser.current_url, os.environ["TEST_DOMAIN"] + "?model=aarhusai-start")
        WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, "chat-input-container")))

        # Admin settings open as a modal on /; only admins get the admin tabs.
        helpers.open_page(browser, "admin/settings")
        WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '[aria-controls="tab-admin-general"]'))
        )


if __name__ == "__main__":
    unittest.main()

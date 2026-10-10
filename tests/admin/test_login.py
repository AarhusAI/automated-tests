import os
import unittest

from selenium.common.exceptions import TimeoutException
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

        # Non-admins are redirected from the admin settings to /; an admin stays.
        admin_url = os.environ["TEST_DOMAIN"] + "admin/settings"
        helpers.open_page(browser, "admin/settings")
        with self.assertRaises(TimeoutException):
            WebDriverWait(browser, 5).until(lambda d: not d.current_url.startswith(admin_url))


if __name__ == "__main__":
    unittest.main()

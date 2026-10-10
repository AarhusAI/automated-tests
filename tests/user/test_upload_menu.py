import os
import unittest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import dotenv

from tests import helpers

dotenv.load_dotenv()


class TestUserUploadMenu(helpers.BrowserTestCase):
    def test_user_cannot_capture_images(self):
        browser = self.browser
        helpers.open_chat(browser, os.environ["USER_USERNAME"], os.environ["USER_PASSWORD"])

        browser.find_element(By.ID, "input-menu-button").click()
        WebDriverWait(browser, 5).until(EC.visibility_of_element_located((
            By.XPATH, "//*[normalize-space(text())='Upload Files' or normalize-space(text())='Upload filer']"
        )))

        browser.implicitly_wait(0)  # asserting absence; don't wait 5s per lookup
        self.assertFalse(browser.find_elements(
            By.XPATH, "//*[normalize-space(text())='Capture' or normalize-space(text())='Optag']"
        ))
        self.assertFalse(browser.find_elements(By.ID, "camera-input"))


if __name__ == "__main__":
    unittest.main()

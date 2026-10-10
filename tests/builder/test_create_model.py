import os
import unittest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import dotenv

from tests import helpers

dotenv.load_dotenv()

FIXTURE_FILE = os.path.join(os.path.dirname(__file__), "..", "fixtures", "test_document.txt")


class TestBuilderCreateModel(helpers.BrowserTestCase):
    def test_builder_can_create_and_share_specialist(self):
        browser = self.browser
        helpers.login(browser, os.environ["BUILDER_USERNAME"], os.environ["BUILDER_PASSWORD"])
        helpers.delete_test_data(browser)
        self.addCleanup(helpers.delete_test_data, browser)

        helpers.create_knowledge(browser, "autotest-knowledge", FIXTURE_FILE)
        helpers.create_model(browser, "autotest-specialist", "autotest-knowledge")

        browser.find_element(By.CSS_SELECTOR, 'input[placeholder="Search Models"]').send_keys("autotest-specialist")
        WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.ID, "model-item-autotest-specialist"))
        )


if __name__ == "__main__":
    unittest.main()

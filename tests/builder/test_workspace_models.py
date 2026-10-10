import os
import unittest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import dotenv

from tests import helpers

dotenv.load_dotenv()

MODEL_ROWS = (By.CSS_SELECTOR, '[id^="model-item-"]')


class TestBuilderWorkspaceModels(helpers.BrowserTestCase):
    def test_builder_can_search_models(self):
        browser = self.browser
        helpers.login(browser, os.environ["BUILDER_USERNAME"], os.environ["BUILDER_PASSWORD"])
        helpers.open_page(browser, "workspace/models")

        WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, "model-item-aarhusai-start")))
        total = len(browser.find_elements(*MODEL_ROWS))

        browser.find_element(By.CSS_SELECTOR, 'input[placeholder="Search Models"]').send_keys("AarhusAI start")
        WebDriverWait(browser, 10).until(lambda d: len(d.find_elements(*MODEL_ROWS)) < total)
        self.assertTrue(browser.find_element(By.ID, "model-item-aarhusai-start").is_displayed())

    def test_builder_can_see_import_and_export(self):
        browser = self.browser
        helpers.login(browser, os.environ["BUILDER_USERNAME"], os.environ["BUILDER_PASSWORD"])
        helpers.open_page(browser, "workspace/models")

        browser.find_element(By.CSS_SELECTOR, 'button[aria-label="Open create menu"]').click()
        for label in ("Import JSON", "Export JSON"):
            WebDriverWait(browser, 5).until(EC.element_to_be_clickable((
                By.XPATH, f"//button[.//*[normalize-space(text())='{label}'] or normalize-space()='{label}']"
            )))


if __name__ == "__main__":
    unittest.main()

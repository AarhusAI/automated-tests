import os
import unittest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import dotenv

from tests import helpers

dotenv.load_dotenv()


class TestUserWebSearch(helpers.BrowserTestCase):
    def test_user_can_enable_web_search_and_find_mayor_of_aarhus(self):
        browser = self.browser
        helpers.open_chat(browser, os.environ["USER_USERNAME"], os.environ["USER_PASSWORD"], model="BA-gpt-oss-120b")

        browser.find_element(By.ID, "integration-menu-button").click()

        WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//button[contains(normalize-space(.), 'Værktøjer') or contains(normalize-space(.), 'Tools')]",
            ))
        ).click()

        # The row button carries the toggle state in aria-pressed; the inner
        # role="switch" is inert (display-only). The enabled state persists
        # per user across sessions, so only click when it is currently off.
        web_search_row = WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//button[@aria-pressed]"
                "[.//*[normalize-space(text())='websearch']]",
            ))
        )
        if web_search_row.get_attribute("aria-pressed") != "true":
            web_search_row.click()
        WebDriverWait(browser, 5).until(
            lambda _: web_search_row.get_attribute("aria-pressed") == "true"
        )

        response = helpers.send_prompt(browser, "Hvem er borgmester i Aarhus?", timeout=120)
        self.assertIn("Anders Winnerskjold", response)


if __name__ == "__main__":
    unittest.main()

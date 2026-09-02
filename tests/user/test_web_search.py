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


class TestUserWebSearch(unittest.TestCase):
    def setUp(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        self.browser = Chrome(options=options)
        self.browser.implicitly_wait(5)

    def tearDown(self):
        self.browser.quit()

    def test_user_can_enable_web_search_and_find_mayor_of_aarhus(self):
        browser = self.browser

        helpers.login(browser, os.environ["USER_USERNAME"], os.environ["USER_PASSWORD"])
        helpers.wait_for_app(browser)

        browser.find_element(By.ID, "integration-menu-button").click()

        WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//button[contains(normalize-space(.), 'Værktøjer')]",
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

        chat_input = browser.find_element(By.ID, "chat-input")
        chat_input.click()
        chat_input.send_keys("Hvem er borgmester i Aarhus?")
        browser.find_element(By.ID, "send-message-button").click()

        WebDriverWait(browser, 120).until(
            lambda d: d.find_element(By.ID, "response-content-container").text.strip() != ""
            and not d.find_elements(By.ID, "stop-response-button")
        )

        response = browser.find_element(By.ID, "response-content-container").text
        self.assertIn("Anders Winnerskjold", response)


if __name__ == "__main__":
    unittest.main()

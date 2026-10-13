import os
import unittest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import dotenv

from tests import helpers

dotenv.load_dotenv()

# The tools on staging; not yet confirmed by the project lead as the expected list.
EXPECTED_TOOLS = [
    "websearch",
    "eventdatabase",
    "retsinformation",
    "EU founding portal",
    "Office documents",
]


class TestUserTools(helpers.BrowserTestCase):
    def test_user_can_see_available_tools(self):
        browser = self.browser
        helpers.open_chat(browser, os.environ["USER_USERNAME"], os.environ["USER_PASSWORD"])

        browser.find_element(By.ID, "integration-menu-button").click()
        WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//button[contains(normalize-space(.), 'Værktøjer') or contains(normalize-space(.), 'Tools')]",
            ))
        ).click()

        for tool in EXPECTED_TOOLS:
            WebDriverWait(browser, 5).until(EC.visibility_of_element_located((
                By.XPATH, f"//button[@aria-pressed][.//*[normalize-space(text())='{tool}']]"
            )))


if __name__ == "__main__":
    unittest.main()

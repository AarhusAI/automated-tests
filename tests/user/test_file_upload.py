import os
import unittest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import dotenv

from tests import helpers

dotenv.load_dotenv()

FIXTURE_FILE = os.path.join(os.path.dirname(__file__), "..", "fixtures", "test_document.txt")


class TestUserFileUpload(helpers.BrowserTestCase):
    def test_user_can_upload_file_and_ask_about_content(self):
        browser = self.browser
        helpers.open_chat(browser, os.environ["USER_USERNAME"], os.environ["USER_PASSWORD"])

        file_input = browser.find_element(By.CSS_SELECTOR, 'input[type="file"][multiple]')
        browser.execute_script("arguments[0].removeAttribute('hidden')", file_input)
        file_input.send_keys(os.path.abspath(FIXTURE_FILE))

        # Wait for the file chip to appear and its upload spinner to be
        # replaced by the document icon. The check must be scoped to the
        # chip: the page permanently contains spinner styles elsewhere.
        WebDriverWait(browser, 30).until(lambda d: d.execute_script(
            "const chip = [...document.querySelectorAll('button')]"
            "    .find(el => el.textContent.includes(arguments[0]));"
            "return !!chip && !chip.querySelector('style, [class*=\"spinner\"]');",
            os.path.basename(FIXTURE_FILE)
        ))

        response = helpers.send_prompt(
            browser, "What is the secret code word in the uploaded file? Reply with the code word only."
        )
        self.assertIn("BANANA", response.upper())


if __name__ == "__main__":
    unittest.main()

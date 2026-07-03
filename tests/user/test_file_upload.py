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

FIXTURE_FILE = os.path.join(os.path.dirname(__file__), "..", "fixtures", "test_document.txt")


class TestUserFileUpload(unittest.TestCase):
    def setUp(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        self.browser = Chrome(options=options)
        self.browser.implicitly_wait(5)

    def tearDown(self):
        self.browser.quit()

    def test_user_can_upload_file_and_ask_about_content(self):
        browser = self.browser

        helpers.login(browser, os.environ["USER_USERNAME"], os.environ["USER_PASSWORD"])
        helpers.wait_for_app(browser)

        file_input = browser.find_element(By.CSS_SELECTOR, 'input[type="file"][multiple]')
        browser.execute_script("arguments[0].removeAttribute('hidden')", file_input)
        file_input.send_keys(os.path.abspath(FIXTURE_FILE))

        # Wait for the upload spinner to disappear from the DOM
        WebDriverWait(browser, 15).until(lambda d: not d.execute_script(
            "return [...document.querySelectorAll('style')]"
            ".some(s => s.textContent.includes('@keyframes spinner'))"
        ))

        chat_input = browser.find_element(By.ID, "chat-input")
        chat_input.click()
        chat_input.send_keys("What is the secret code word in the uploaded file? Reply with the code word only.")
        browser.find_element(By.ID, "send-message-button").click()

        WebDriverWait(browser, 60).until(
            EC.invisibility_of_element_located((By.ID, "stop-response-button"))
        )

        response = browser.find_element(By.ID, "response-content-container")
        self.assertIn("BANANA", response.text.upper())


if __name__ == "__main__":
    unittest.main()

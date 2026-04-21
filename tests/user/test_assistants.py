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

EXPECTED_ASSISTANTS = [
    "Korrekturlæseren",
    "Det gode stillingsopslag",
    "Opsummering",
    "Klarsprog-bot",
]


class TestUserAssistants(unittest.TestCase):
    def setUp(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        self.browser = Chrome(options=options)
        self.browser.implicitly_wait(5)

    def tearDown(self):
        self.browser.quit()

    def test_available_assistants_are_listed(self):
        browser = self.browser

        helpers.login(browser, os.environ["USER_USERNAME"], os.environ["USER_PASSWORD"])
        helpers.wait_for_app(browser)

        chat_input = browser.find_element(By.ID, "chat-input")
        chat_input.click()
        chat_input.send_keys("Hvilke assistenter kan jeg få adgang til?")
        browser.find_element(By.ID, "send-message-button").click()

        WebDriverWait(browser, 60).until(
            EC.invisibility_of_element_located((By.ID, "stop-response-button"))
        )

        response = browser.find_element(By.ID, "response-content-container").text
        for assistant in EXPECTED_ASSISTANTS:
            self.assertIn(assistant, response)


if __name__ == "__main__":
    unittest.main()

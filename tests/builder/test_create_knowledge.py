import os
import unittest

from selenium.webdriver.support.wait import WebDriverWait
import dotenv

from tests import helpers

dotenv.load_dotenv()

FIXTURE_FILE = os.path.join(os.path.dirname(__file__), "..", "fixtures", "test_document.txt")


class TestBuilderCreateKnowledge(helpers.BrowserTestCase):
    def test_builder_can_create_knowledge_and_upload_file(self):
        browser = self.browser
        helpers.login(browser, os.environ["BUILDER_USERNAME"], os.environ["BUILDER_PASSWORD"])
        helpers.delete_test_data(browser)
        self.addCleanup(helpers.delete_test_data, browser)

        helpers.create_knowledge(browser, "autotest-knowledge", FIXTURE_FILE)

        browser.find_element(*helpers.knowledge_file_row(FIXTURE_FILE)).click()
        # The preview re-renders while loading, so query it fresh on every poll.
        WebDriverWait(browser, 10).until(lambda d: d.execute_script(
            "return document.querySelector('textarea[aria-label=\"File content\"]')?.value.includes('BANANA');"
        ))


if __name__ == "__main__":
    unittest.main()

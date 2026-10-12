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

        # Clicking the file before the server has processed it opens nothing; the row looks the same either way,
        # so click again on each poll until the preview shows. Query it fresh since it re-renders while loading.
        def preview_has_code_word(d):
            if d.execute_script(
                "return document.querySelector('textarea[aria-label=\"File content\"]')?.value.includes('BANANA');"
            ):
                return True
            d.find_element(*helpers.knowledge_file_row(FIXTURE_FILE)).click()
            return False

        WebDriverWait(browser, 30, poll_frequency=2).until(preview_has_code_word)


if __name__ == "__main__":
    unittest.main()

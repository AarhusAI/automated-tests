import os
import unittest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import dotenv

from tests import helpers

dotenv.load_dotenv()

FIXTURE_FILE = os.path.join(os.path.dirname(__file__), "..", "fixtures", "test_document.txt")
PROMPT = "Hvad er det hemmelige kodeord i den vedhæftede viden? Svar kun med kodeordet."


class TestBuilderKnowledgeDeletion(helpers.BrowserTestCase):
    def ask_user(self, user_browser):
        helpers.open_page(user_browser, "?model=autotest-specialist")
        return helpers.send_prompt(user_browser, PROMPT, timeout=120).upper()

    def test_deleted_knowledge_is_no_longer_answered(self):
        builder = self.browser
        helpers.login(builder, os.environ["BUILDER_USERNAME"], os.environ["BUILDER_PASSWORD"])
        helpers.delete_test_data(builder)
        self.addCleanup(helpers.delete_test_data, builder)

        helpers.create_knowledge(builder, "autotest-knowledge", FIXTURE_FILE)
        knowledge_url = builder.current_url
        helpers.create_model(builder, "autotest-specialist", "autotest-knowledge")

        user = helpers.new_browser(*self.chrome_args)
        self.addCleanup(user.quit)
        helpers.login(user, os.environ["USER_USERNAME"], os.environ["USER_PASSWORD"])
        self.assertIn("BANANA", self.ask_user(user))

        builder.get(knowledge_url)
        helpers.wait_for_app(builder)
        builder.find_element(
            By.XPATH, f"{helpers.knowledge_file_row(FIXTURE_FILE)[1]}/following-sibling::*//button"
        ).click()
        builder.find_element(By.XPATH, "//button[normalize-space()='Delete']").click()
        WebDriverWait(builder, 10).until(EC.invisibility_of_element_located(helpers.knowledge_file_row(FIXTURE_FILE)))

        # ponytail: one retry for the vector index lagging behind the delete; poll if it stays flaky.
        response = self.ask_user(user)
        if "BANANA" in response:
            response = self.ask_user(user)
        self.assertNotIn("BANANA", response)


if __name__ == "__main__":
    unittest.main()

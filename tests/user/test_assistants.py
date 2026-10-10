import os
import unittest

import dotenv

from tests import helpers

dotenv.load_dotenv()

EXPECTED_ASSISTANTS = [
    "Korrekturlæseren",
    "Det gode stillingsopslag",
    "Opsummering",
    "Klarsprog-bot",
]


class TestUserAssistants(helpers.BrowserTestCase):
    def test_available_assistants_are_listed(self):
        browser = self.browser
        helpers.open_chat(browser, os.environ["USER_USERNAME"], os.environ["USER_PASSWORD"])

        response = helpers.send_prompt(browser, "Hvilke assistenter kan jeg få adgang til?")
        for assistant in EXPECTED_ASSISTANTS:
            self.assertIn(assistant, response)


if __name__ == "__main__":
    unittest.main()

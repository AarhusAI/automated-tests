import os

from tests import helpers

EXPECTED_ASSISTANTS = [
    "Korrekturlæseren",
    "Det gode stillingsopslag",
    "Opsummering",
    "Klarsprog-bot",
]


def test_available_assistants_are_listed(page):
    helpers.open_chat(page, os.environ["USER_USERNAME"], os.environ["USER_PASSWORD"])

    assert page.url == os.environ["TEST_DOMAIN"] + "?model=aarhusai-start"
    response = helpers.send_prompt(page, "Hvilke assistenter kan jeg få adgang til?")
    for assistant in EXPECTED_ASSISTANTS:
        assert assistant in response

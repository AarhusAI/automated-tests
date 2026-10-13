import os

from playwright.sync_api import expect

from tests import helpers

FIXTURE_FILE = os.path.join(os.path.dirname(__file__), "..", "fixtures", "test_document.txt")
PROMPT = "Hvad er det hemmelige kodeord i den vedhæftede viden? Svar kun med kodeordet."


def ask_user(user):
    helpers.open_page(user, "?model=autotest-specialist")
    return helpers.send_prompt(user, PROMPT, timeout=120).upper()


def test_deleted_knowledge_is_no_longer_answered(page, request, new_context):
    helpers.login(page, os.environ["BUILDER_USERNAME"], os.environ["BUILDER_PASSWORD"])
    helpers.delete_test_data(page)
    request.addfinalizer(lambda: helpers.delete_test_data(page))

    helpers.create_knowledge(page, "autotest-knowledge", FIXTURE_FILE)
    knowledge_url = page.url
    helpers.create_model(page, "autotest-specialist", "autotest-knowledge")

    # A second isolated session in the same browser; the new_context fixture closes it at teardown.
    user = new_context().new_page()
    helpers.login(user, os.environ["USER_USERNAME"], os.environ["USER_PASSWORD"])
    assert "BANANA" in ask_user(user)

    page.goto(knowledge_url)
    helpers.wait_for_app(page)
    row = helpers.knowledge_file_row(FIXTURE_FILE)
    page.locator(row + "/following-sibling::*//button").first.click()
    page.locator("//button[normalize-space()='Delete']").first.click()
    expect(page.locator(row)).to_be_hidden(timeout=10_000)

    # ponytail: one retry for the vector index lagging behind the delete; poll if it stays flaky.
    response = ask_user(user)
    if "BANANA" in response:
        response = ask_user(user)
    assert "BANANA" not in response

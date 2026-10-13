import os

from playwright.sync_api import expect

from tests import helpers

FIXTURE_FILE = os.path.join(os.path.dirname(__file__), "..", "fixtures", "test_document.txt")
PROMPT = (
    "Hvad er det hemmelige kodeord i den vedhæftede viden? Svar kun med kodeordet. "
    "Hvis du ikke kan finde det, svar kun: VED IKKE"
)


def ask_specialist(page):
    helpers.open_page(page, "?model=autotest-specialist")
    return helpers.send_prompt(page, PROMPT, timeout=120).upper()


def test_deleted_knowledge_is_no_longer_answered(page, request):
    helpers.login(page, os.environ["BUILDER_USERNAME"], os.environ["BUILDER_PASSWORD"])
    helpers.delete_test_data(page)
    request.addfinalizer(lambda: helpers.delete_test_data(page))

    helpers.create_knowledge(page, "autotest-knowledge", FIXTURE_FILE)
    knowledge_url = page.url
    # Asking before the server has processed the file gets "no code word found".
    assert helpers.knowledge_file_preview_contains(page, FIXTURE_FILE, "BANANA")
    # With a tool attached the model searches knowledge through tools and does not find the file.
    helpers.create_model(page, "autotest-specialist", "autotest-knowledge", websearch=False)

    assert "BANANA" in ask_specialist(page)

    page.goto(knowledge_url)
    helpers.wait_for_app(page)
    row = helpers.knowledge_file_row(FIXTURE_FILE)
    page.locator(row + "/following-sibling::*//button").first.click()
    page.locator("//button[normalize-space()='Delete']").first.click()
    expect(page.locator(row)).to_be_hidden(timeout=10_000)

    response = ask_specialist(page)
    if "BANANA" in response:
        response = ask_specialist(page)
    assert "BANANA" not in response
    assert "VED IKKE" in response

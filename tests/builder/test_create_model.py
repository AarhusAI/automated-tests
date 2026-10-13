import os

from playwright.sync_api import expect

from tests import helpers

FIXTURE_FILE = os.path.join(os.path.dirname(__file__), "..", "fixtures", "test_document.txt")


def test_builder_can_create_and_share_specialist(page, request):
    helpers.login(page, os.environ["BUILDER_USERNAME"], os.environ["BUILDER_PASSWORD"])
    helpers.delete_test_data(page)
    request.addfinalizer(lambda: helpers.delete_test_data(page))

    helpers.create_knowledge(page, "autotest-knowledge", FIXTURE_FILE)
    helpers.create_model(page, "autotest-specialist", "autotest-knowledge")

    page.locator('input[placeholder="Search Models"]').fill("autotest-specialist")
    expect(page.locator("#model-item-autotest-specialist")).to_be_visible(timeout=10_000)

    # The edit page shows every field create_model set.
    helpers.open_page(page, "workspace/models/edit?id=autotest-specialist")
    expect(page.locator("#model-selector-workspace-base-model-button")).to_have_text(
        os.environ.get("BASE_MODEL", helpers.DEFAULT_BASE_MODEL)
    )
    expect(page.locator('textarea[aria-label^="Add a short description"]')).to_have_value(helpers.MODEL_DESCRIPTION)
    expect(page.locator('textarea[aria-label^="Write your model system prompt"]')).to_have_value(
        helpers.MODEL_SYSTEM_PROMPT
    )
    expect(page.locator(f"//button[span[normalize-space()='{helpers.MODEL_TAG}']]").first).to_be_attached()
    expect(page.locator("//div[normalize-space(text())='Tools']/../..").first).to_contain_text("Websearch", use_inner_text=True)

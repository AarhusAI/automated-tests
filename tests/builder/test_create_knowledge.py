import os
import time

from tests import helpers

FIXTURE_FILE = os.path.join(os.path.dirname(__file__), "..", "fixtures", "test_document.txt")


def test_builder_can_create_knowledge_and_upload_file(page, request):
    helpers.login(page, os.environ["BUILDER_USERNAME"], os.environ["BUILDER_PASSWORD"])
    helpers.delete_test_data(page)
    request.addfinalizer(lambda: helpers.delete_test_data(page))

    helpers.create_knowledge(page, "autotest-knowledge", FIXTURE_FILE)

    # Clicking the file before the server has processed it opens nothing; the row looks the same either way,
    # so click again on each poll until the preview shows.
    def preview_has_code_word():
        return page.evaluate(
            "document.querySelector('textarea[aria-label=\"File content\"]')?.value.includes('BANANA') ?? false"
        )

    deadline = time.monotonic() + 30
    while not preview_has_code_word() and time.monotonic() < deadline:
        page.locator(helpers.knowledge_file_row(FIXTURE_FILE)).first.click()
        page.wait_for_timeout(2000)
    assert preview_has_code_word()

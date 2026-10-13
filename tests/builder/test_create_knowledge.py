import os

from tests import helpers

FIXTURE_FILE = os.path.join(os.path.dirname(__file__), "..", "fixtures", "test_document.txt")


def test_builder_can_create_knowledge_and_upload_file(page, request):
    helpers.login(page, os.environ["BUILDER_USERNAME"], os.environ["BUILDER_PASSWORD"])
    helpers.delete_test_data(page)
    request.addfinalizer(lambda: helpers.delete_test_data(page))

    helpers.create_knowledge(page, "autotest-knowledge", FIXTURE_FILE)

    assert helpers.knowledge_file_preview_contains(page, FIXTURE_FILE, "BANANA")

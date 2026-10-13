import os

from tests import helpers

FIXTURE_FILE = os.path.join(os.path.dirname(__file__), "..", "fixtures", "test_document.txt")


def test_user_can_upload_file_and_ask_about_content(page):
    helpers.open_chat(page, os.environ["USER_USERNAME"], os.environ["USER_PASSWORD"])

    page.locator('input[type="file"][multiple]').first.set_input_files(os.path.abspath(FIXTURE_FILE))

    # Wait for the file chip to appear and its upload spinner to be
    # replaced by the document icon. The check must be scoped to the
    # chip: the page permanently contains spinner styles elsewhere.
    page.wait_for_function(
        "name => {"
        "  const chip = [...document.querySelectorAll('button')].find(el => el.textContent.includes(name));"
        "  return !!chip && !chip.querySelector('style, [class*=\"spinner\"]');"
        "}",
        arg=os.path.basename(FIXTURE_FILE),
        timeout=30_000,
    )

    response = helpers.send_prompt(
        page, "What is the secret code word in the uploaded file? Reply with the code word only."
    )
    assert "BANANA" in response.upper()

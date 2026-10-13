import os

from playwright.sync_api import expect

from tests import helpers


def test_user_cannot_capture_images(page):
    helpers.open_chat(page, os.environ["USER_USERNAME"], os.environ["USER_PASSWORD"])

    page.locator("#input-menu-button").click()
    expect(page.locator(
        "//*[normalize-space(text())='Upload Files' or normalize-space(text())='Upload filer']"
    ).first).to_be_visible(timeout=5_000)

    # count() does not wait, so this asserts absence once the menu is open.
    assert page.locator("//*[normalize-space(text())='Capture' or normalize-space(text())='Optag']").count() == 0

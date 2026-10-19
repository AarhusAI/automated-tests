import os

from playwright.sync_api import expect

from tests import helpers

# The tools on staging; not yet confirmed by the project lead as the expected list.
EXPECTED_TOOLS = [
    "websearch",
    "eventdatabase",
    "retsinformation",
    "EU founding portal",
    "Office documents",
]


def test_user_can_see_available_tools(page):
    helpers.open_chat(page, os.environ["USER_USERNAME"], os.environ["USER_PASSWORD"])

    page.locator("#integration-menu-button").click()
    page.locator(
        "//button[contains(normalize-space(.), 'Værktøjer') or contains(normalize-space(.), 'Tools')]"
    ).first.click(timeout=5_000)

    for tool in EXPECTED_TOOLS:
        expect(
            page.locator(f"//button[@aria-pressed][.//*[normalize-space(text())='{tool}']]")
        ).to_be_visible(timeout=5_000)

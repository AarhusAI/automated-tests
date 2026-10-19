import os

from playwright.sync_api import expect

from tests import helpers


def test_user_can_enable_web_search_and_find_mayor_of_aarhus(page):
    helpers.open_chat(page, os.environ["USER_USERNAME"], os.environ["USER_PASSWORD"], model="BA-gpt-oss-120b")

    page.locator("#integration-menu-button").click()
    page.locator(
        "//button[contains(normalize-space(.), 'Værktøjer') or contains(normalize-space(.), 'Tools')]"
    ).first.click(timeout=5_000)

    # The row button carries the toggle state in aria-pressed; the inner
    # role="switch" is inert (display-only). The enabled state persists
    # per user across sessions, so only click when it is currently off.
    web_search_row = page.locator("//button[@aria-pressed][.//*[normalize-space(text())='websearch']]")
    web_search_row.wait_for(timeout=5_000)
    if web_search_row.get_attribute("aria-pressed") != "true":
        web_search_row.click()
    expect(web_search_row).to_have_attribute("aria-pressed", "true", timeout=5_000)

    response = helpers.send_prompt(page, "Hvem er borgmester i Aarhus?", timeout=120)
    assert "Anders Winnerskjold" in response

from playwright.sync_api import expect

from tests import helpers


def test_login_page_info(page):
    helpers.open_page(page, "")

    expect(page.locator("body")).to_contain_text(
        "Du skal anmode om adgang til AarhusAI (AI-platform) i Aarhus Kommunes systemregister, "
        "før du logger på første gang."
    )

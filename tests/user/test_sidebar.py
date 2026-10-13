import re
import os

from playwright.sync_api import expect

from tests import helpers

LOGO = 'img[src*="designguide.aarhus.dk"]'


def test_user_can_see_logo_and_name_in_expanded_sidebar(page):
    helpers.open_chat(page, os.environ["USER_USERNAME"], os.environ["USER_PASSWORD"])

    # The sidebar starts collapsed in a fresh browser context.
    page.locator('button[aria-label="Open Sidebar"]:visible').first.click()

    logo = page.locator(LOGO)
    name = page.locator('button[aria-label="User menu"]')
    expect(logo).to_be_visible()
    expect(name).to_have_text(re.compile(r"\S"))

    viewport = page.viewport_size
    logo_box = logo.bounding_box()
    name_box = name.bounding_box()
    assert logo_box["x"] < 100
    assert logo_box["y"] + logo_box["height"] > viewport["height"] - 100
    assert name_box["y"] + name_box["height"] <= logo_box["y"]

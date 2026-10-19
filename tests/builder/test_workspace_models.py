import os

from playwright.sync_api import expect

from tests import helpers

MODEL_ROWS = '[id^="model-item-"]'


def test_builder_can_search_models(page):
    helpers.login(page, os.environ["BUILDER_USERNAME"], os.environ["BUILDER_PASSWORD"])
    helpers.open_page(page, "workspace/models")

    expect(page.locator("#model-item-aarhusai-start")).to_be_visible(timeout=10_000)
    total = page.locator(MODEL_ROWS).count()

    page.locator('input[placeholder="Search Models"]').fill("AarhusAI start")
    page.wait_for_function(
        f"n => document.querySelectorAll('{MODEL_ROWS}').length < n", arg=total, timeout=10_000
    )
    expect(page.locator("#model-item-aarhusai-start")).to_be_visible()


def test_builder_can_see_import_and_export(page):
    helpers.login(page, os.environ["BUILDER_USERNAME"], os.environ["BUILDER_PASSWORD"])
    helpers.open_page(page, "workspace/models")

    page.locator('button[aria-label="Open create menu"]').click()
    for label in ("Import JSON", "Export JSON"):
        expect(page.locator(
            f"//button[.//*[normalize-space(text())='{label}'] or normalize-space()='{label}']"
        ).first).to_be_visible(timeout=5_000)

import os

import pytest
from playwright.sync_api import expect

from tests import helpers

pytestmark = pytest.mark.skipif(not os.environ.get("ADMIN_USERNAME"), reason="ADMIN_USERNAME/ADMIN_PASSWORD not set")


def test_login_as_admin(page):
    helpers.open_chat(page, os.environ["ADMIN_USERNAME"], os.environ["ADMIN_PASSWORD"])

    assert page.url == os.environ["TEST_DOMAIN"] + "?model=aarhusai-start"
    expect(page.locator("#chat-input-container")).to_be_visible(timeout=10_000)

    # Admin settings open as a modal on /; only admins get the admin tabs.
    helpers.open_page(page, "admin/settings")
    expect(page.locator('[aria-controls="tab-admin-general"]')).to_be_visible(timeout=10_000)

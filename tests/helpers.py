import json
import os
import re

from playwright.sync_api import Error, expect

# UI language depends on account/locale, not the browser; match both.
REGENERATE_BUTTON = 'button[aria-label="Regenerer"], button[aria-label="Regenerate"]'

# Fields create_model fills in; env BASE_MODEL overrides the base model.
DEFAULT_BASE_MODEL = "AarhusAI-default-v2"
MODEL_DESCRIPTION = "Automated test specialist"
MODEL_TAG = "autotest-tag"
MODEL_SYSTEM_PROMPT = "Answer questions using the attached knowledge. Be brief."


def login(page, username, password):
    domain = os.environ["TEST_DOMAIN"]
    page.goto(domain)
    page.locator("#email").fill(username)
    page.locator("#password").fill(password)
    page.locator('button[type="submit"]').click()
    page.wait_for_url(domain, timeout=10_000)
    # Navigating before the app has loaded the session bounces workspace pages back to "/".
    wait_for_app(page)


def wait_for_app(page):
    page.locator("#splash-screen").wait_for(state="hidden", timeout=30_000)
    # The feedback widget overlays the right edge and intercepts clicks on row menus.
    page.evaluate("document.getElementById('itk-feedback')?.remove()")


def open_chat(page, username, password, model="aarhusai-start"):
    login(page, username, password)
    page.goto(os.environ["TEST_DOMAIN"] + "?model=" + model)
    wait_for_app(page)


def send_prompt(page, text, timeout=60):
    page.locator("#chat-input").fill(text)
    page.locator("#send-message-button").click()
    page.locator(REGENERATE_BUTTON).first.wait_for(state="visible", timeout=timeout * 1000)
    return page.locator("#response-content-container").first.inner_text()


def open_page(page, path):
    page.goto(os.environ["TEST_DOMAIN"] + path)
    wait_for_app(page)


def create_knowledge(page, name, file_path):
    """Create a knowledge base through the UI and upload one file into it. Leaves the page on the knowledge base."""
    open_page(page, "workspace/knowledge/create")
    page.locator('input[placeholder="Name your knowledge base"]').fill(name)
    page.locator('textarea[placeholder="Describe your knowledge base and objectives"]').fill("Automated test")
    page.locator('button[type="submit"]').first.click()
    page.wait_for_url(re.compile(r"/workspace/knowledge/[0-9a-f-]{36}$"), timeout=10_000)
    # The file input ignores files until the knowledge base has loaded.
    page.locator('input[placeholder="Search Collection"]').wait_for(timeout=10_000)

    page.locator("#files-input").set_input_files(os.path.abspath(file_path))
    page.locator(knowledge_file_row(file_path)).wait_for(timeout=30_000)


def knowledge_file_row(file_path):
    return f"//button[.//*[contains(text(), '{os.path.basename(file_path)}')]]"


def create_model(page, name, knowledge):
    """Create a specialist on env BASE_MODEL (default "AarhusAI-default-v2") with `knowledge` and the `websearch`
    tool attached, tagged `autotest-tag`, shared read-only with a group.

    The group is env SHARE_GROUP (default "Builder"); the user account must be a member to see the specialist.
    """
    group = os.environ.get("SHARE_GROUP", "Builder")
    base_model = os.environ.get("BASE_MODEL", DEFAULT_BASE_MODEL)
    open_page(page, "workspace/models/create")
    page.locator("#model-selector-workspace-base-model-button").click()
    page.locator(f'button[aria-label="Select {base_model} model"]').click()

    page.locator("//*[normalize-space(text())='Select Knowledge']").first.click()
    page.locator(f"//button[.//*[normalize-space(text())='{knowledge}']]").first.click()

    page.locator("//*[normalize-space(text())='Select Tool']").first.click()
    page.locator("//button[span[normalize-space()='websearch']]").click()
    page.keyboard.press("Escape")

    page.locator("//button[normalize-space()='Access']").click()
    page.locator("//button[normalize-space()='Add Access']").click()
    dialog = page.locator("//*[@role='dialog'][.//input[@placeholder='Search']]")
    dialog.locator('input[placeholder="Search"]').fill(group)
    dialog.locator(f"xpath=.//button[.//div[normalize-space(text())='{group}']]").first.click()
    dialog.locator("xpath=.//button[normalize-space()='Add']").click()
    # The access list now shows the group.
    expect(page.locator(
        f"//*[@role='dialog'][.//*[normalize-space()='Access List']]//*[normalize-space(text())='{group}']"
    ).first).to_be_visible(timeout=5_000)
    page.keyboard.press("Escape")
    expect(page.locator('[role="dialog"]').first).to_be_hidden(timeout=5_000)

    page.locator('input[placeholder="Model Name"]').fill(name)
    page.locator('textarea[aria-label^="Add a short description"]').fill(MODEL_DESCRIPTION)
    tag = page.locator('input[placeholder="Add a tag..."]')
    tag.fill(MODEL_TAG)
    tag.press("Enter")
    page.locator('textarea[aria-label^="Write your model system prompt"]').fill(MODEL_SYSTEM_PROMPT)
    page.locator("//button[normalize-space()='Save & Create']").click()
    page.wait_for_url(os.environ["TEST_DOMAIN"] + "workspace/models", timeout=10_000)


def api(page, method, path, body=None):
    # ponytail: only for cleanup of test data; the flows under test go through the UI.
    result = page.evaluate(
        """async ([method, path, body]) => {
            try {
                const r = await fetch(path, {method, body: body && JSON.stringify(body), headers: {
                    'Authorization': 'Bearer ' + localStorage.token, 'Content-Type': 'application/json'}});
                return {ok: r.ok, status: r.status, text: await r.text()};
            } catch (e) {
                return {ok: false, status: 0, text: String(e)};
            }
        }""",
        [method, path, body],
    )
    if not result["ok"]:
        raise RuntimeError(f"{method} {path} failed: {result['status']} {result['text'][:200]}")
    return json.loads(result["text"]) if result["text"] else None


def delete_test_data(page):
    """Delete the logged-in user's `autotest-*` models and knowledge bases, including their files."""
    for model in api(page, "GET", "/api/v1/models/list?query=autotest-")["items"]:
        if model["id"].startswith("autotest-"):
            api(page, "POST", "/api/v1/models/model/delete", {"id": model["id"]})
    for knowledge in api(page, "GET", "/api/v1/knowledge/search?query=autotest-")["items"]:
        if knowledge["name"].startswith("autotest-"):
            for file in api(page, "GET", f"/api/v1/knowledge/{knowledge['id']}/files")["items"]:
                api(page, "DELETE", f"/api/v1/files/{file['id']}")
            api(page, "DELETE", f"/api/v1/knowledge/{knowledge['id']}/delete")


def save_screenshot(item, page, failed):
    """Called from the conftest report hook with the pytest item and whether its call phase failed."""
    # Toggles: SCREENSHOTS=0 disables the PNG (default on); HTML_DUMP=1 enables the page HTML (default off).
    screenshot = os.environ.get("SCREENSHOTS", "1") != "0"
    html = os.environ.get("HTML_DUMP", "0") != "0"
    if not (screenshot or html):
        return
    directory = os.path.join(os.path.dirname(__file__), "..", "screenshots", "failed" if failed else "success")
    os.makedirs(directory, exist_ok=True)
    path = os.path.abspath(os.path.join(directory, f"{item.module.__name__}.{item.originalname}"))
    try:
        if screenshot:
            page.screenshot(path=path + ".png")
        if html:
            with open(path + ".html", "w", encoding="utf-8") as f:
                f.write(page.content())
        if failed:
            print(f"\nFailure artifacts saved: {path}.*")
    except Error:
        pass

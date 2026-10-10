import json
import os
import unittest

from selenium.common.exceptions import WebDriverException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# UI language depends on account/locale, not the browser; match both.
REGENERATE_BUTTON = 'button[aria-label="Regenerer"], button[aria-label="Regenerate"]'

# Base model for created specialists.
BASE_MODEL = "BA-gpt-oss-120b"


def new_browser(*args):
    options = Options()
    options.add_argument("--window-size=1920,1080")
    for arg in args:
        options.add_argument(arg)
    browser = Chrome(options=options)
    browser.implicitly_wait(5)
    return browser


def login(browser, username, password):
    domain = os.environ["TEST_DOMAIN"]
    browser.get(domain)
    browser.find_element(value="email").send_keys(username)
    browser.find_element(value="password").send_keys(password)
    browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    WebDriverWait(browser, 10).until(EC.url_to_be(domain))


def wait_for_app(browser):
    WebDriverWait(browser, 30).until(
        EC.invisibility_of_element_located((By.ID, "splash-screen"))
    )
    # The feedback widget overlays the right edge and intercepts clicks on row menus.
    browser.execute_script("document.getElementById('itk-feedback')?.remove()")


def open_chat(browser, username, password, model="aarhusai-start"):
    login(browser, username, password)
    browser.get(os.environ["TEST_DOMAIN"] + "?model=" + model)
    wait_for_app(browser)


def send_prompt(browser, text, timeout=60):
    chat_input = browser.find_element(By.ID, "chat-input")
    chat_input.click()
    chat_input.send_keys(text)
    browser.find_element(By.ID, "send-message-button").click()
    WebDriverWait(browser, timeout).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, REGENERATE_BUTTON))
    )
    return browser.find_element(By.ID, "response-content-container").text


def open_page(browser, path):
    browser.get(os.environ["TEST_DOMAIN"] + path)
    wait_for_app(browser)


def create_knowledge(browser, name, file_path):
    """Create a knowledge base through the UI and upload one file into it. Leaves the browser on its page."""
    open_page(browser, "workspace/knowledge/create")
    browser.find_element(By.CSS_SELECTOR, 'input[placeholder="Name your knowledge base"]').send_keys(name)
    browser.find_element(
        By.CSS_SELECTOR, 'textarea[placeholder="Describe your knowledge base and objectives"]'
    ).send_keys("Automated test")
    browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    WebDriverWait(browser, 10).until(EC.url_matches(r"/workspace/knowledge/[0-9a-f-]{36}$"))
    # The file input ignores files until the knowledge base has loaded.
    WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Search Collection"]'))
    )

    file_input = browser.find_element(By.ID, "files-input")
    browser.execute_script("arguments[0].removeAttribute('hidden')", file_input)
    file_input.send_keys(os.path.abspath(file_path))
    WebDriverWait(browser, 30).until(EC.element_to_be_clickable(knowledge_file_row(file_path)))


def knowledge_file_row(file_path):
    return By.XPATH, f"//button[.//*[contains(text(), '{os.path.basename(file_path)}')]]"


def create_model(browser, name, knowledge):
    """Create a specialist on BASE_MODEL with `knowledge` attached, shared read-only with a group.

    The group is env SHARE_GROUP (default "Builder"); the user account must be a member to see the specialist.
    """
    group = os.environ.get("SHARE_GROUP", "Builder")
    open_page(browser, "workspace/models/create")
    browser.find_element(By.ID, "model-selector-workspace-base-model-button").click()
    browser.find_element(By.CSS_SELECTOR, f'button[aria-label="Select {BASE_MODEL} model"]').click()

    browser.find_element(By.XPATH, "//*[normalize-space(text())='Select Knowledge']").click()
    browser.find_element(By.XPATH, f"//button[.//*[normalize-space(text())='{knowledge}']]").click()

    browser.find_element(By.XPATH, "//button[normalize-space()='Access']").click()
    browser.find_element(By.XPATH, "//button[normalize-space()='Add Access']").click()
    dialog = browser.find_element(By.XPATH, "//*[@role='dialog'][.//input[@placeholder='Search']]")
    dialog.find_element(By.CSS_SELECTOR, 'input[placeholder="Search"]').send_keys(group)
    dialog.find_element(By.XPATH, f".//button[.//div[normalize-space(text())='{group}']]").click()
    dialog.find_element(By.XPATH, ".//button[normalize-space()='Add']").click()
    # The access list now shows the group.
    WebDriverWait(browser, 5).until(EC.visibility_of_element_located((
        By.XPATH, f"//*[@role='dialog'][.//*[normalize-space()='Access List']]//*[normalize-space(text())='{group}']"
    )))
    browser.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
    WebDriverWait(browser, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '[role="dialog"]')))

    browser.find_element(By.CSS_SELECTOR, 'input[placeholder="Model Name"]').send_keys(name)
    browser.find_element(
        By.CSS_SELECTOR, 'textarea[aria-label^="Add a short description"]'
    ).send_keys("Automated test specialist")
    browser.find_element(
        By.CSS_SELECTOR, 'textarea[aria-label^="Write your model system prompt"]'
    ).send_keys("Answer questions using the attached knowledge. Be brief.")
    save = browser.find_element(By.XPATH, "//button[normalize-space()='Save & Create']")
    browser.execute_script("arguments[0].scrollIntoView()", save)
    save.click()
    WebDriverWait(browser, 10).until(EC.url_to_be(os.environ["TEST_DOMAIN"] + "workspace/models"))


def api(browser, method, path, body=None):
    # ponytail: only for cleanup of test data; the flows under test go through the UI.
    result = browser.execute_async_script(
        "const [method, path, body, done] = arguments;"
        "fetch(path, {method, body: body && JSON.stringify(body), headers: {"
        "    'Authorization': 'Bearer ' + localStorage.token, 'Content-Type': 'application/json'}})"
        "  .then(async r => done({ok: r.ok, status: r.status, text: await r.text()}))"
        "  .catch(e => done({ok: false, status: 0, text: String(e)}));",
        method, path, body,
    )
    if not result["ok"]:
        raise RuntimeError(f"{method} {path} failed: {result['status']} {result['text'][:200]}")
    return json.loads(result["text"]) if result["text"] else None


def delete_test_data(browser):
    """Delete the logged-in user's `autotest-*` models and knowledge bases, including their files."""
    for model in api(browser, "GET", "/api/v1/models/list?query=autotest-")["items"]:
        if model["id"].startswith("autotest-"):
            api(browser, "POST", "/api/v1/models/model/delete", {"id": model["id"]})
    for knowledge in api(browser, "GET", "/api/v1/knowledge/search?query=autotest-")["items"]:
        if knowledge["name"].startswith("autotest-"):
            for file in api(browser, "GET", f"/api/v1/knowledge/{knowledge['id']}/files")["items"]:
                api(browser, "DELETE", f"/api/v1/files/{file['id']}")
            api(browser, "DELETE", f"/api/v1/knowledge/{knowledge['id']}/delete")


def save_screenshot(test, browser):
    # Toggles: SCREENSHOTS=0 disables the PNG (default on); HTML_DUMP=1 enables the page HTML (default off).
    screenshot = os.environ.get("SCREENSHOTS", "1") != "0"
    html = os.environ.get("HTML_DUMP", "0") != "0"
    if not (screenshot or html):
        return
    # ponytail: reads unittest's private _outcome; no public "did this test fail" API in tearDown
    result = test._outcome.result
    failed = any(t is test for t, _ in result.errors + result.failures)
    directory = os.path.join(os.path.dirname(__file__), "..", "screenshots", "failed" if failed else "success")
    os.makedirs(directory, exist_ok=True)
    path = os.path.abspath(os.path.join(directory, test.id()))
    try:
        if screenshot:
            browser.save_screenshot(path + ".png")
        if html:
            with open(path + ".html", "w", encoding="utf-8") as f:
                f.write(browser.page_source)
        if failed:
            print(f"\nFailure artifacts saved: {path}.*")
    except WebDriverException:
        pass


class BrowserTestCase(unittest.TestCase):
    chrome_args = ("--headless",)

    def setUp(self):
        self.browser = new_browser(*self.chrome_args)
        # Cleanups run LIFO after tearDown, so ones a test registers still have a live browser.
        self.addCleanup(self.browser.quit)

    def tearDown(self):
        save_screenshot(self, self.browser)

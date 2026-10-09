import os
import unittest

from selenium.common.exceptions import WebDriverException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# UI language depends on account/locale, not the browser; match both.
REGENERATE_BUTTON = 'button[aria-label="Regenerer"], button[aria-label="Regenerate"]'


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


def open_chat(browser, username, password, model="aarhusai-start"):
    login(browser, username, password)
    browser.get(os.environ["TEST_DOMAIN"] + "?model=" + model)
    wait_for_app(browser)


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

    def tearDown(self):
        save_screenshot(self, self.browser)
        self.browser.quit()

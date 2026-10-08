import os

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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


SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "..", "screenshots")


def screenshot_on_failure(test, browser):
    # ponytail: reads unittest's private _outcome; no public "did this test fail" API in tearDown
    result = test._outcome.result
    if not any(t is test for t, _ in result.errors + result.failures):
        return
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    path = os.path.abspath(os.path.join(SCREENSHOT_DIR, f"{test.id()}.png"))
    try:
        browser.save_screenshot(path)
        print(f"\nScreenshot saved: {path}")
    except WebDriverException:
        pass

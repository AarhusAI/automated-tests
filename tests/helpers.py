import os

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

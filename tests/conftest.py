import dotenv
import pytest

from tests import helpers

# Loaded before the test modules are imported, so module-level skipif sees .env values.
dotenv.load_dotenv()


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "viewport": {"width": 1920, "height": 1080}}


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    report = yield
    # Runs before any fixture teardown, so the page still shows the end state and test data still exists.
    if report.when == "call" and "page" in item.funcargs:
        helpers.save_screenshot(item, item.funcargs["page"], report.failed)
    return report

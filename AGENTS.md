# Repository Guidelines

## Project Overview

End-to-end Selenium tests for the **AarhusAI web UI**, a Danish-language chat UI that appears to be based on
Open WebUI. The tests run against a **live deployment** set by `TEST_DOMAIN`. They log in as real accounts and
assert on real LLM output. Nothing is mocked and there is no app code in this repo.

## Architecture & Data Flow

- **Runner:** stdlib `unittest`. There is no pytest, no `conftest.py` and no markers.
- **Driver:** synchronous Selenium using `selenium.webdriver.Chrome`. There is no async code and no Playwright.
- **Config:** `.env` is read by `dotenv.load_dotenv()` at the top of each test module. In Docker it is passed with
  `env_file: .env`.
- **Flow of a test:** `helpers.BrowserTestCase.setUp` creates Chrome → `helpers.open_chat(browser, user, pw)`
  (login, open `?model=aarhusai-start`, wait for the app) → interact with the UI → wait for the response to finish →
  `self.assert*` → `tearDown` saves a screenshot and quits the browser.
- **Model:** every test opens `?model=aarhusai-start` after login; `test_web_search` opens `?model=BA-gpt-oss-120b`.
- `tests/helpers.py`:
  - `BrowserTestCase` is the base class for every test. `setUp` builds Chrome from `chrome_args` (default
    `("--headless",)`) via `new_browser()`, `tearDown` calls `save_screenshot` and `browser.quit()`.
  - `new_browser(*args)` creates Chrome with `--window-size=1920,1080` plus `args` and `implicitly_wait(5)`.
  - `login()` opens `TEST_DOMAIN`, fills `#email` and `#password`, clicks `button[type="submit"]`, then waits 10s
    for `EC.url_to_be(TEST_DOMAIN)`.
  - `wait_for_app()` waits 30s for `#splash-screen` to become invisible.
  - `open_chat(browser, user, pw, model="aarhusai-start")` runs `login`, opens `?model=<model>` and calls
    `wait_for_app`.
  - `save_screenshot()` writes `screenshots/{success,failed}/<test id>.png` (`SCREENSHOTS=0` disables, default on)
    and optionally `.html` (`HTML_DUMP=1`, default off). It reads unittest's private `_outcome` to detect failure.
    `screenshots/` is gitignored.
- **Response complete** means the regenerate button (`helpers.REGENERATE_BUTTON`) is visible. It only renders after
  the answer finishes, unlike waiting for `#stop-response-button` to vanish, which passes before the button appears.
  Use 60s, or 120s for web search. Then read `#response-content-container`.
- **Locale:** headless runs render the UI in English (`Regenerate`, not `Regenerer`). Setting
  `intl.accept_languages=da` did not change this; `da-DK` and a stored account locale were not tested. Selectors
  that use labels match both the Danish and the English text.
- `exploration/explore.py` is a standalone CLI for writing selectors. It opens a page, can log in and click
  elements, and writes `exploration/explore_screenshot.png` and `exploration/explore_page.html`. These outputs are
  **not gitignored**, so do not commit them. It inserts the repo root into `sys.path` and reuses `tests.helpers`.

## Key Directories

- `tests/user/`: tests for the normal-user role: `test_login`, `test_chat`, `test_assistants`, `test_file_upload`,
  `test_web_search`, `test_dictate`.
- `tests/builder/`: tests for the builder role (`test_login`).
- `tests/fixtures/`:
  - `test_document.txt` contains the code word `BANANA`.
  - `dictation_sample.wav` says "Hej med dig".
- `exploration/`: page-inspection helper.
- `Dockerfile`: installs Chromium, chromedriver and Xvfb.

Every test directory needs an `__init__.py` so discovery and `from tests import helpers` work.

## Development Commands

```bash
cp .env.example .env            # fill TEST_DOMAIN (with trailing slash) + credentials
uv sync
uv run python -m unittest                                   # all tests
uv run python -m unittest tests.user.test_chat              # one module
uv run python -m unittest tests.user.test_chat.TestUserChat.test_user_can_send_prompt_and_receive_response

# Docker (Chromium + xvfb-run entrypoint, repo bind-mounted at /app)
docker compose build
docker compose run --rm tests
docker compose run --rm tests python -m unittest tests.user.test_chat

# Selector exploration (--click repeatable; "//" or "(" prefix = XPath, else CSS)
uv run python exploration/explore.py <url_path> --login user|builder --click "#integration-menu-button"

# Taskfile shortcuts (all Docker-based; SCREENSHOTS/HTML_DUMP forwarded from the shell)
task setup                      # cp .env.example .env (skipped if .env exists)
task build                      # docker compose build with the host's UID/GID as build args
task tests                      # rm -rf screenshots/* then run all tests
task test TEST=tests.user.test_chat   # one module/method (default tests.user.test_chat)
task explore -- <url_path> --login user --click "#sel"
task lint                       # markdownlint on **/*.md + CHANGELOG.md must differ from origin/main
task lint:markdown -- --fix     # autofix markdown
```

There is no build step, formatter or type checker for the Python code. The only lint is markdownlint and the
changelog check, both run via `task lint` and as GitHub Actions on pull requests. Every PR must touch `CHANGELOG.md`.

## Code Conventions & Common Patterns

- **One `TestCase` per module, one feature per module.**
  - Files: `tests/<role>/test_<feature>.py`.
  - Classes: `Test<Role><Feature>`, e.g. `TestUserChat` or `TestBuilderLogin`.
  - Methods: `test_<role>_can_<action>...` or `test_login_as_<role>`.
- **Subclass `helpers.BrowserTestCase`.** Follow `tests/user/test_chat.py`:
  - Do not write `setUp`/`tearDown`. Override `chrome_args` only when the browser needs other flags
    (`test_dictate` drops `--headless` and adds the fake-media flags).
  - Start each test with `helpers.open_chat(browser, user, pw)`; pass `model=` to open another model.
  - The module ends with `if __name__ == "__main__": unittest.main()`.
- **Credentials:** read them as `os.environ["USER_USERNAME"]`, `os.environ["USER_PASSWORD"]`,
  `os.environ["BUILDER_USERNAME"]` and `os.environ["BUILDER_PASSWORD"]`. Never hardcode them.
- **Login tests** call `open_chat`, then assert
  `browser.current_url == os.environ["TEST_DOMAIN"] + "?model=aarhusai-start"` and wait for `#chat-input-container`
  to be visible. All other tests also call `wait_for_app` after login.
- **Selectors:**
  - Prefer `By.ID`, e.g. `chat-input`, `send-message-button`, `voice-input-button`.
  - Match visible text with XPath and `normalize-space`. The text is Danish, e.g. `Værktøjer`.
  - Use CSS selectors for attributes.
- **Waits:** use `WebDriverWait(...).until(EC...)` or a lambda. A `time.sleep` appears only where unavoidable, e.g.
  while dictation records.
- **Persistent per-user UI state:** toggles such as web search keep their state per user. Check `aria-pressed` before
  clicking.
- **Hidden file inputs:** remove the `hidden` attribute with `execute_script`, then call
  `send_keys(os.path.abspath(path))`.
- **Fixture paths:** `os.path.join(os.path.dirname(__file__), "..", "fixtures", name)`.
- **Assertions:** use `self.assertEqual`, `self.assertIn` and `self.assertTrue`. LLM output is non-deterministic, so
  assert on a key substring, e.g. `"BANANA"` in `response.text.upper()`, not on exact text.

## Important Files

- `tests/helpers.py`: the shared `BrowserTestCase`, `new_browser`, `login`, `wait_for_app`, `open_chat`,
  `save_screenshot` and `REGENERATE_BUTTON`.
- `tests/user/test_chat.py`: the reference test template.
- `tests/user/test_dictate.py`: the only non-headless test. It uses Chrome fake-media flags plus
  `--use-file-for-fake-audio-capture`, so it needs a display (Xvfb in Docker).
- `.env.example` defines `TEST_DOMAIN`, `BUILDER_USERNAME`, `BUILDER_PASSWORD`, `USER_USERNAME`, `USER_PASSWORD`,
  `SCREENSHOTS` and `HTML_DUMP`.
- `docker-compose.yml` defines a single `tests` service. It needs `init: true`, otherwise `xvfb-run` hangs. It passes
  `UID`/`GID` build args (default 1042) and forwards `SCREENSHOTS`/`HTML_DUMP` from the shell.
- `Dockerfile`:
  - Base image `python:3.13-slim-bookworm` with uv 0.11.
  - The venv is at `/opt/venv`, outside the bind mount.
  - Chromium flags `--no-sandbox --disable-dev-shm-usage` via `/etc/chromium.d/docker-flags`.
  - Runs as user `deploy`. Its uid/gid come from the `UID`/`GID` build args (default 1042; `task build` passes the
    host's so bind-mount writes are owned by the host user).
- `README.md` has a `## Tests` section that lists every test as `#### [path](path)` followed by
  `- **\`test_name\`** — description`. Update it when you add or rename a test.

## Runtime/Tooling Preferences

- Python **3.13**, set in `.python-version` and as `requires-python >=3.13`.
- Use **uv** as the package manager and always run through `uv run`. `uv.lock` is committed. Docker uses
  `uv sync --frozen --no-dev`.
- This is a virtual uv project with no `[build-system]`, so it is not an installable package.
- Runtime dependencies are only `selenium` and `python-dotenv`. Do not add pytest or other frameworks unless asked.
- Local runs need Chrome or Chromium plus a matching driver. Selenium Manager resolves the driver.

## Testing & QA

- The tests are the product. Each test is one user-visible flow on the live site.
- There are no coverage targets and no unit tests.
- Tests need network access, a reachable `TEST_DOMAIN` and valid accounts. A failure can come from the deployment or
  the model, not only from the test code.
- The UI and the expected answers are in Danish, e.g. the assistant names `Korrekturlæseren` and `Klarsprog-bot`, and
  the strings `Hej med dig` and `Anders Winnerskjold`.
- To verify a change, run the specific module with `uv run python -m unittest tests.<role>.test_<feature>`.

# Repository Guidelines

## Project Overview

End-to-end Playwright tests for the **AarhusAI web UI**, a Danish-language chat UI that appears to be based on
Open WebUI. The tests run against a **live deployment** set by `TEST_DOMAIN`. They log in as real accounts and
assert on real LLM output. Nothing is mocked and there is no app code in this repo.

## Architecture & Data Flow

- **Runner:** pytest with the `pytest-playwright` plugin. Tests are plain functions that take the plugin's `page`
  fixture. There are no `unittest` classes.
- **Driver:** synchronous Playwright (`playwright.sync_api`) on Chromium, headless by default (`--headed` to watch).
  There is no async code and no Selenium.
- **Config:** `.env` is read once by `dotenv.load_dotenv()` at the top of `tests/conftest.py`, before the test modules
  are imported, so module-level `skipif` sees it. In Docker it is passed with `env_file: .env`.
- **Flow of a test:** the plugin creates a browser context and `page` → `helpers.open_chat(page, user, pw)` (login,
  open `?model=aarhusai-start`, wait for the app) → interact with the UI → wait for the response to finish →
  bare `assert` or `expect(...)` → the conftest report hook saves a screenshot → finalizers run (data cleanup) → the
  plugin closes the context.
- **Model:** chat tests open `?model=aarhusai-start` after login; `test_web_search` opens `?model=BA-gpt-oss-120b`.
  Workspace tests call `login` then `open_page(page, "workspace/...")`.
- `tests/conftest.py`:
  - Overrides the session-scoped `browser_context_args` to add a 1920x1080 viewport.
  - A `pytest_runtest_makereport` wrapper hook calls `helpers.save_screenshot(item, page, failed)` after the call
    phase, before any fixture teardown, so the screenshot shows the end state and runs before data cleanup. Setup
    failures get no screenshot.
  - No default timeout is set. Playwright's 30s action timeout applies; pass explicit `timeout=` (ms) where the old
    waits had one. Do not call `set_default_timeout`, it would also cap `page.goto`.
- `tests/helpers.py`:
  - `login()` opens `TEST_DOMAIN`, fills `#email` and `#password`, clicks `button[type="submit"]`, then waits 10s
    with `page.wait_for_url(TEST_DOMAIN)` and calls `wait_for_app`. Without that wait, workspace URLs opened right
    after login redirect to `/`.
  - `wait_for_app()` waits 30s for `#splash-screen` to be hidden, then removes the `#itk-feedback` widget
    (it intercepts clicks on row menus).
  - `open_chat(page, user, pw, model="aarhusai-start")` runs `login`, opens `?model=<model>` and calls
    `wait_for_app`. `open_page(page, path)` opens `TEST_DOMAIN + path` and calls `wait_for_app`.
  - `send_prompt(page, text, timeout=60)` fills `#chat-input`, sends, waits for the response to finish and returns
    its `inner_text()`.
  - `create_knowledge(page, name, file_path)` and `create_model(page, name, knowledge)` run the workspace
    create flows through the UI. Both share read-only with env `SHARE_GROUP` (default `Builder`) via
    `add_group_access(page, group)`. Specialists use base model env `BASE_MODEL` (default `AarhusAI-default-v2`), get
    tag `MODEL_TAG`, description `MODEL_DESCRIPTION`, system prompt `MODEL_SYSTEM_PROMPT` and the `websearch` tool,
    attached.
  - `knowledge_file_row(file_path)` returns an XPath string for the file's row on a knowledge base page.
  - `knowledge_file_preview_contains(page, file_path, text)` clicks the file until its preview contains `text`, i.e.
    the server has processed it, and returns whether it did within 30s. Wait on it before asking about the file.
  - `api(page, method, path, body=None)` calls the Open WebUI API with the page's token via `page.evaluate`. Use it
    **only for cleanup**; `delete_test_data(page)` deletes the logged-in user's `autotest-*` models and knowledge
    bases with their files. Tests that create data call it after login and register it with
    `request.addfinalizer(lambda: helpers.delete_test_data(page))`.
  - `save_screenshot(item, page, failed)` writes `screenshots/{success,failed}/<module>.<function>.png`, e.g.
    `tests.user.test_chat.test_user_can_send_prompt_and_receive_response.png` (`SCREENSHOTS=0` disables, default
    on) and optionally `.html` (`HTML_DUMP=1`, default off). `screenshots/` is gitignored.
- **Response complete** means the regenerate button (`helpers.REGENERATE_BUTTON`) is visible. It only renders after
  the answer finishes, unlike waiting for `#stop-response-button` to vanish, which passes before the button appears.
  Use 60s, or 120s for web search. Then read `#response-content-container` (`.first`).
- **Locale:** headless runs render the UI in English (`Regenerate`, not `Regenerer`). Setting
  `intl.accept_languages=da` did not change this; `da-DK` and a stored account locale were not tested. Selectors
  that use labels match both the Danish and the English text.
- `exploration/explore.py` is a standalone CLI for writing selectors. It starts its own Playwright Chromium, opens a
  page, can log in and click elements, and writes `exploration/explore_screenshot.png` and
  `exploration/explore_page.html`. These outputs are **not gitignored**, so do not commit them. It inserts the
  repo root into `sys.path` and reuses `tests.helpers`.

## Key Directories

- `tests/user/`: tests for the normal-user role: `test_login`, `test_login_page_info`, `test_accessibility_statement`,
  `test_chat`, `test_assistants`, `test_file_upload`, `test_web_search`, `test_dictate`, `test_tools`, `test_upload_menu`,
  `test_tts`, `test_sidebar`.
- `tests/builder/`: tests for the builder role: `test_login`, `test_workspace_models`, `test_create_knowledge`,
  `test_create_model`, `test_knowledge_deletion`.
- `tests/admin/`: tests for the admin role (`test_login`), skipped unless `ADMIN_USERNAME` is set.
- `tests/fixtures/`:
  - `test_document.txt` contains the code word `BANANA`.
  - `dictation_sample.wav` says "Hej med dig".
- `exploration/`: page-inspection helper.
- `Dockerfile`: installs Playwright's Chromium with its system dependencies.

Every test directory needs an `__init__.py` so `from tests import helpers` works (pytest puts the repo root on
`sys.path`).

## Development Commands

```bash
cp .env.example .env            # fill TEST_DOMAIN (with trailing slash) + credentials
uv sync
uv run playwright install chromium                          # once, downloads the browser
uv run pytest                                               # all tests
uv run pytest tests/user/test_chat.py                       # one module
uv run pytest tests/user/test_chat.py::test_user_can_send_prompt_and_receive_response
uv run pytest tests/user/test_chat.py --headed              # watch the browser

# Docker (Playwright Chromium, repo bind-mounted at /app)
docker compose build
docker compose run --rm tests
docker compose run --rm tests pytest tests/user/test_chat.py

# Selector exploration (--click repeatable; "//" or "(" prefix = XPath, else CSS)
uv run python exploration/explore.py <url_path> --login user|builder --click "#integration-menu-button"

# Taskfile shortcuts (Docker-based except test:headed/test:debug; SCREENSHOTS/HTML_DUMP forwarded from the shell)
task setup                      # cp .env.example .env (skipped if .env exists)
task build                      # docker compose build with the host's UID/GID as build args
task tests                      # rm -rf screenshots/* then run all tests
task test TEST=tests/user/test_chat.py::test_...   # one file/test (default tests/user/test_chat.py)
task test:headed TEST=tests/user/test_chat.py -- --slowmo 500   # local, not Docker; visible browser
task test:debug TEST=tests/user/test_chat.py::test_...          # local; step through in the Playwright Inspector
task test:list                  # print the test node ids usable as TEST=
task explore -- <url_path> --login user --click "#sel"
task lint                       # markdownlint on **/*.md + CHANGELOG.md must differ from origin/main
task lint:markdown -- --fix     # autofix markdown
```

There is no build step, formatter or type checker for the Python code. The only lint is markdownlint and the
changelog check, both run via `task lint` and as GitHub Actions on pull requests. Every PR must touch `CHANGELOG.md`.

## Code Conventions & Common Patterns

- **One feature per module, plain test functions.**
  - Files: `tests/<role>/test_<feature>.py`.
  - Functions: `test_<role>_can_<action>...(page)` or `test_login_as_<role>(page)`.
- **Follow `tests/user/test_chat.py`:**
  - Take the `page` fixture; add `request` when registering cleanup. Do not create browsers yourself.
  - Start each test with `helpers.open_chat(page, user, pw)`; pass `model=` to open another model.
  - `test_dictate` is the only module that overrides `page`: it launches its own browser from `browser_type` with
    the fake-media flags, merged into `browser_type_launch_args`.
  - Skip a whole module with `pytestmark = pytest.mark.skipif(...)` (see `tests/admin/test_login.py`).
- **Credentials:** read them as `os.environ["USER_USERNAME"]`, `os.environ["USER_PASSWORD"]`,
  `os.environ["BUILDER_USERNAME"]` and `os.environ["BUILDER_PASSWORD"]`. Never hardcode them.
- **Login tests** call `open_chat`, then assert
  `page.url == os.environ["TEST_DOMAIN"] + "?model=aarhusai-start"` and
  `expect(page.locator("#chat-input-container")).to_be_visible()`. All other tests also call `wait_for_app` after login.
- **Selectors:**
  - Prefer ids: `page.locator("#chat-input")`, `#send-message-button`, `#voice-input-button`.
  - Match visible text with XPath and `normalize-space`. The text is Danish, e.g. `Værktøjer`.
  - Use CSS selectors for attributes.
  - Locators are strict: an action or `expect` on a locator that matches several elements fails. Add `.first` where
    several can match (generic text XPaths, `#response-content-container`, `button[type="submit"]`).
  - Playwright treats a selector as XPath only when it starts with `//` or `..`. Prefix `xpath=` for one that
    starts with `(`, and for a relative `.//` under a chained locator.
- **Waits:** locator actions auto-wait. Use `expect(locator).to_be_visible/to_have_text/...(timeout=ms)` for
  assertions on the page, `locator.wait_for` for a plain wait and `page.wait_for_function` for JS conditions. A
  `time.sleep` appears only where unavoidable, e.g. while dictation records.
- **Persistent per-user UI state:** toggles such as web search keep their state per user. Check `aria-pressed` before
  clicking.
- **File inputs:** `locator.set_input_files(path)` works on hidden inputs too.
- **Live values:** read input/textarea values with `input_value()` or `expect(...).to_have_value(...)`;
  `get_attribute("value")` returns the HTML attribute. `expect(...).to_contain_text` uses `textContent`; pass
  `use_inner_text=True` when CSS `text-transform` changes the visible text.
- **Fixture paths:** `os.path.join(os.path.dirname(__file__), "..", "fixtures", name)`.
- **Assertions:** bare `assert` on Python values, `expect(...)` on locators (it retries). LLM output is
  non-deterministic, so assert on a key substring, e.g. `"BANANA" in response.upper()`, not on exact text.

## Important Files

- `tests/conftest.py`: `.env` loading, the viewport and the screenshot hook.
- `tests/helpers.py`: `login`, `wait_for_app`, `open_chat`, `open_page`, `send_prompt`, `create_knowledge`,
  `knowledge_file_row`, `knowledge_file_preview_contains`, `add_group_access`, `create_model`, `api`,
  `delete_test_data`, `save_screenshot` and `REGENERATE_BUTTON`.
- `tests/user/test_chat.py`: the reference test template.
- `tests/user/test_dictate.py`: overrides `page` to launch Chromium with fake-media flags plus
  `--use-file-for-fake-audio-capture`. It runs headless; no display is needed.
- `.env.example` defines `TEST_DOMAIN`, `BUILDER_USERNAME`, `BUILDER_PASSWORD`, `USER_USERNAME`, `USER_PASSWORD`,
  `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `SHARE_GROUP`, `BASE_MODEL`, `SCREENSHOTS` and `HTML_DUMP`.
- `docker-compose.yml` defines a single `tests` service. It passes `UID`/`GID` build args (default 1042) and
  forwards `SCREENSHOTS`/`HTML_DUMP` from the shell.
- `Dockerfile`:
  - Base image `python:3.13-slim-bookworm` with uv 0.11.
  - The venv is at `/opt/venv`, outside the bind mount.
  - `playwright install --with-deps chromium` into `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`. Playwright launches
    Chromium with `--no-sandbox` and `--disable-dev-shm-usage` itself.
  - Runs as user `deploy`. Its uid/gid come from the `UID`/`GID` build args (default 1042; `task build` passes the
    host's so bind-mount writes are owned by the host user).
  - `CMD ["pytest"]`; pytest finds `tests/` via `testpaths` in `pyproject.toml`.
- `README.md` has a `## Tests` section that lists every test as `#### [path](path)` followed by
  `- **\`test_name\`** — description`. Update it when you add or rename a test.

## Runtime/Tooling Preferences

- Python **3.13**, set in `.python-version` and as `requires-python >=3.13`.
- Use **uv** as the package manager and always run through `uv run`. `uv.lock` is committed. Docker uses
  `uv sync --frozen --no-dev`.
- This is a virtual uv project with no `[build-system]`, so it is not an installable package.
- Runtime dependencies are only `pytest-playwright` (pulls in `pytest` and `playwright`) and `python-dotenv`. Do not
  add other frameworks or pytest plugins unless asked.
- Local runs need the Playwright browser: `uv run playwright install chromium`.

## Testing & QA

- The tests are the product. Each test is one user-visible flow on the live site.
- There are no coverage targets and no unit tests.
- Tests need network access, a reachable `TEST_DOMAIN` and valid accounts. A failure can come from the deployment or
  the model, not only from the test code.
- The UI and the expected answers are in Danish, e.g. the assistant names `Korrekturlæseren` and `Klarsprog-bot`, and
  the strings `Hej med dig` and `Anders Winnerskjold`.
- To verify a change, run the specific module with `uv run pytest tests/<role>/test_<feature>.py`.

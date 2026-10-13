# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog], and this project adheres to [Semantic Versioning].

## [Unreleased]

### Fixed

- `helpers.login` waits for the app to load, so workspace pages opened right after login no longer redirect to `/`.
- `helpers.create_model` uses base model env `BASE_MODEL` (default `AarhusAI-default-v2`); `BA-gpt-oss-120b` is no
  longer offered as a base model to the builder.
- `test_user_cannot_capture_images` no longer asserts that `#camera-input` is absent; the hidden input is always in
  the DOM.
- `test_builder_can_create_knowledge_and_upload_file` clicks the file again until the preview loads, since a click
  before the server has processed the file opens nothing.

### Changed

- Switched the suite from Selenium and `unittest` to pytest-playwright. Tests are plain functions that take the
  `page` fixture, `tests/conftest.py` replaces `BrowserTestCase` and takes the screenshots, and screenshot names drop
  the class (`tests.user.test_chat.test_...`). Run with `uv run pytest` after `uv run playwright install chromium`.
- The dictation test runs headless, so the Docker image drops Xvfb, the `xvfb-run` entrypoint and `init: true`, and
  installs Playwright's Chromium instead of Debian's chromium and chromedriver.
- `task test` takes a pytest node id (`TEST=tests/user/test_chat.py::test_...`) and `task test:list` prints node ids.

- `helpers.create_model` also adds the tag `autotest-tag` and the `websearch` tool. The specialist test now checks
  the base model, description, tag, system prompt and tool on the model's edit page.

### Added

- Tests for tools listing, no image capture in the upload menu, read aloud (TTS), workspace model search and
  import/export, knowledge creation with upload, specialist creation and sharing, knowledge deletion end to end, and
  admin login.
- `helpers.send_prompt`, `create_knowledge`, `create_model` and `delete_test_data` (API cleanup of `autotest-*` data).
- README section on recording a flow with Chrome DevTools Recorder or Selenium IDE (Firefox) and turning it into a
  new or updated test.
- `ADMIN_USERNAME`, `ADMIN_PASSWORD` and `SHARE_GROUP` in `.env.example`; `admin` login in `exploration/explore.py`.
- GitHub Actions workflows for markdownlint and changelog checks, plus markdownlint config.
- `AGENTS.md` with repository guidelines for coding agents.
- Taskfile with `setup`, `build`, `tests`, `test`, `test:list`, `explore` and `lint` tasks.
- Screenshots on test completion, split into `screenshots/success` and `screenshots/failed`. Can be disabled with
  `SCREENSHOTS=0`. Optional HTML dump of the page with `HTML_DUMP=1`.
- Repeatable `--click` option in `exploration/explore.py` for interacting with the page before capture.
- Docker setup with Chromium, chromedriver and Xvfb, run through `docker compose`.
- Selenium tests for login (user and builder), chat, assistants, file upload, web search and dictation.
- `exploration/explore.py` helper for inspecting pages and writing selectors.

[Keep a Changelog]: https://keepachangelog.com/en/1.1.0/
[Semantic Versioning]: https://semver.org/spec/v2.0.0.html
[unreleased]: https://github.com/AarhusAI/automated-tests/compare/main...HEAD

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog], and this project adheres to [Semantic Versioning].

## [Unreleased]

### Added

- GitHub Actions workflows for markdownlint and changelog checks, plus markdownlint config.
- `AGENTS.md` with repository guidelines for coding agents.
- Taskfile with `setup`, `build`, `tests`, `test`, `explore` and `lint` tasks.
- Screenshots on test completion, split into `screenshots/success` and `screenshots/failed`. Can be disabled with
  `SCREENSHOTS=0`. Optional HTML dump of the page with `HTML_DUMP=1`.
- Repeatable `--click` option in `exploration/explore.py` for interacting with the page before capture.
- Docker setup with Chromium, chromedriver and Xvfb, run through `docker compose`.
- Selenium tests for login (user and builder), chat, assistants, file upload, web search and dictation.
- `exploration/explore.py` helper for inspecting pages and writing selectors.

### Changed

- `AGENTS.md` reformatted to pass markdownlint.
- README updated to describe every test and the Taskfile commands.
- Login tests wait for the chat input to load before asserting.
- Web search test toggles the web search tool and submits by click.
- Upload and web search tests updated for the new Open WebUI version.
- Docker image uses the host's UID/GID as build args so bind-mount writes are owned by the host user.

[Keep a Changelog]: https://keepachangelog.com/en/1.1.0/
[Semantic Versioning]: https://semver.org/spec/v2.0.0.html
[unreleased]: https://github.com/AarhusAI/automated-tests/compare/main...HEAD

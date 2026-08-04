# automated-tests

Selenium-based end-to-end tests for the AarhusAI web UI.

## Setup

1. Copy `.env.example` to `.env` and fill in `TEST_DOMAIN` plus the role credentials.
2. Install dependencies (uv): `uv sync`.
3. Run all tests: `uv run python -m unittest`.

## Docker

The image (`.docker/app/Dockerfile`) bundles Python 3.13, Chromium, chromedriver and Xvfb, so tests run without any local browser setup. Credentials are passed from `.env` at runtime (not baked into the image).

- Build: `docker compose build`
- Run all tests: `docker compose run --rm tests`
- Run a single test: `docker compose run --rm tests python -m unittest tests.user.test_chat`
- Explore a page: `docker compose run --rm tests python exploration/explore.py <url_path> --login user` (outputs land in `exploration/` on the host via the bind mount)

The container entrypoint wraps commands in `xvfb-run`, which provides the virtual display the non-headless dictation test needs.

## Tests

### Builder

#### [tests/builder/test_login.py](tests/builder/test_login.py)

- **`test_login_as_builder`** — logs in with builder credentials and asserts the browser lands on `TEST_DOMAIN`.

### User

#### [tests/user/test_login.py](tests/user/test_login.py)

- **`test_login_as_user`** — logs in with user credentials and asserts the browser lands on `TEST_DOMAIN`.

#### [tests/user/test_chat.py](tests/user/test_chat.py)

- **`test_user_can_send_prompt_and_receive_response`** — sends "Say only the word: hello" and asserts a non-empty response is returned.

#### [tests/user/test_assistants.py](tests/user/test_assistants.py)

- **`test_available_assistants_are_listed`** — asks the chatbot which assistants are available and asserts the response lists Korrekturlæseren, Det gode stillingsopslag, Opsummering, and Klarsprog-bot.

#### [tests/user/test_file_upload.py](tests/user/test_file_upload.py)

- **`test_user_can_upload_file_and_ask_about_content`** — uploads `tests/fixtures/test_document.txt`, asks for the secret code word inside, and asserts the response contains "BANANA".

#### [tests/user/test_web_search.py](tests/user/test_web_search.py)

- **`test_user_can_enable_web_search_and_find_mayor_of_aarhus`** — opens the integration menu, toggles on Websøgning, asks who the mayor of Aarhus is, and asserts the response contains "Anders Winnerskjold".

#### [tests/user/test_dictate.py](tests/user/test_dictate.py)

- **`test_user_can_dictate_into_chat_input`** — pipes `tests/fixtures/dictation_sample.wav` into Chrome's fake microphone, clicks the Dikter button, confirms the recording, and asserts the transcribed text "Hej med dig" appears in the chat input.

## Exploration

`exploration/explore.py` is a helper for writing new tests: it navigates to a path (optionally logging in first) and dumps a screenshot plus the rendered page source so selectors can be inspected without running a full test. Pass `--click <selector>` (repeatable; CSS, or XPath if it starts with `//`) to click elements — e.g. open a menu or flip a toggle — before the capture:

```bash
uv run python exploration/explore.py --login user --click "#integration-menu-button"
```

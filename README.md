# Automated tests for AarhusAI

Selenium-based end-to-end tests for the AarhusAI web UI.

## Setup

1. Copy `.env.example` to `.env` (or `task setup`) and fill in `TEST_DOMAIN` (with trailing slash) plus the role
   credentials.
2. Install dependencies (uv): `uv sync`.
3. Run all tests: `uv run python -m unittest`, or a single module/method:
   `uv run python -m unittest tests.user.test_chat`.

Most tests log in, then open `TEST_DOMAIN?model=aarhusai-start` (the web search test uses `?model=BA-gpt-oss-120b`)
before interacting with the UI. The workspace tests open `TEST_DOMAIN/workspace/...` instead.

Tests that create data name it `autotest-*` (`autotest-knowledge`, `autotest-specialist`) and delete every
`autotest-*` model and knowledge base of the builder account, with their files, before and after the test. Created
specialists are shared with the group in `SHARE_GROUP` (default `Builder`); the user account must be a member of it.
The admin tests are skipped unless `ADMIN_USERNAME` is set.

After each test a screenshot is saved to `screenshots/success/<test id>.png` or `screenshots/failed/<test id>.png`
(gitignored, overwritten on each run). In Docker, it lands in `./screenshots/` on the host via the bind mount.
Toggle via env (`.env` or inline): `SCREENSHOTS=0` disables screenshots (default on); `HTML_DUMP=1` also saves the
rendered page source as `<test id>.html` (default off), e.g. `SCREENSHOTS=0 uv run python -m unittest` or
`HTML_DUMP=1 task tests` (docker-compose forwards both from the shell).

## Docker

The image (`Dockerfile`) bundles Python 3.13, Chromium, chromedriver and Xvfb, so tests run without any
local browser setup. Credentials are passed from `.env` at runtime (not baked into the image).

- Build: `docker compose build`
- Run all tests: `docker compose run --rm tests`
- Run a single test: `docker compose run --rm tests python -m unittest tests.user.test_chat`
- Explore a page: `docker compose run --rm tests python exploration/explore.py <url_path> --login user` (outputs land in
  `exploration/` on the host via the bind mount)

The container runs as user `deploy`. The build args `UID`/`GID` default to 1042 (the server's ids); pass your own so
files written to the bind mount (`screenshots/`, `exploration/`) are owned by you. `task build` does this automatically.

The container entrypoint wraps commands in `xvfb-run`, which provides the virtual display the non-headless dictation
test needs. `docker-compose.yml` sets `init: true`; without it `xvfb-run` hangs forever.

## Task

`Taskfile.yml` wraps the Docker commands above (`task --list` shows them):

- `task setup` — copy `.env.example` to `.env` (skipped if `.env` exists)
- `task build` — build the image with the host's UID/GID
- `task tests` — clear `screenshots/` and run all tests
- `task test TEST=tests.user.test_chat` — run one module/method (defaults to `tests.user.test_chat`)
- `task explore -- <url_path> --login user --click "#sel"` — run the exploration script
- `task lint` — run markdownlint on all `.md` files and check that `CHANGELOG.md` differs from `origin/main`
  (`task lint:markdown -- --fix` autofixes)

`SCREENSHOTS`/`HTML_DUMP` set in the shell are forwarded, e.g. `HTML_DUMP=1 task tests`.

## Tests

### Admin

#### [tests/admin/test_login.py](tests/admin/test_login.py)

- **`test_login_as_admin`** — logs in with admin credentials, asserts the same as the other login tests, then opens
  `/admin/settings` and asserts it is not redirected away within 5 s. Skipped when `ADMIN_USERNAME` is unset.

### Builder

#### [tests/builder/test_login.py](tests/builder/test_login.py)

- **`test_login_as_builder`** — logs in with builder credentials, opens `?model=aarhusai-start` and asserts the URL
  matches and the chat input is displayed.

#### [tests/builder/test_workspace_models.py](tests/builder/test_workspace_models.py)

- **`test_builder_can_search_models`** — searches `/workspace/models` for "AarhusAI start" and asserts the row list
  shrinks and still shows the AarhusAI start row.
- **`test_builder_can_see_import_and_export`** — opens the create menu and asserts `Import JSON` and `Export JSON`
  are clickable.

#### [tests/builder/test_create_knowledge.py](tests/builder/test_create_knowledge.py)

- **`test_builder_can_create_knowledge_and_upload_file`** — creates the `autotest-knowledge` knowledge base, uploads
  `tests/fixtures/test_document.txt`, opens the file and asserts the preview contains "BANANA".

#### [tests/builder/test_create_model.py](tests/builder/test_create_model.py)

- **`test_builder_can_create_and_share_specialist`** — creates `autotest-knowledge`, then the `autotest-specialist`
  model on `BA-gpt-oss-120b` with that knowledge, shared with `SHARE_GROUP`, and asserts the workspace search finds
  it.

#### [tests/builder/test_knowledge_deletion.py](tests/builder/test_knowledge_deletion.py)

- **`test_deleted_knowledge_is_no_longer_answered`** — the builder creates `autotest-knowledge` and
  `autotest-specialist`; in a second browser the user asks the specialist for the code word and gets "BANANA". The
  builder then deletes the file from the knowledge base, and the user asks again in a new chat and must not get
  "BANANA" (retried once for index lag). Runs two browsers and takes a few minutes.

### User

#### [tests/user/test_login.py](tests/user/test_login.py)

- **`test_login_as_user`** — logs in with user credentials, opens `?model=aarhusai-start` and asserts the URL matches
  and the chat input is displayed.

#### [tests/user/test_chat.py](tests/user/test_chat.py)

- **`test_user_can_send_prompt_and_receive_response`** — sends "Say only the word: hello" and asserts a non-empty
  response is returned.

#### [tests/user/test_assistants.py](tests/user/test_assistants.py)

- **`test_available_assistants_are_listed`** — asks the chatbot which assistants are available and asserts the response
  lists Korrekturlæseren, Det gode stillingsopslag, Opsummering, and Klarsprog-bot.

#### [tests/user/test_file_upload.py](tests/user/test_file_upload.py)

- **`test_user_can_upload_file_and_ask_about_content`** — uploads `tests/fixtures/test_document.txt`, waits for the
  upload spinner to finish, asks for the secret code word inside, and asserts the response contains "BANANA".

#### [tests/user/test_web_search.py](tests/user/test_web_search.py)

- **`test_user_can_enable_web_search_and_find_mayor_of_aarhus`** — opens the integration menu, opens Værktøjer and
  toggles on the websearch tool (only if not already on; the state persists per user), asks who the mayor of Aarhus is,
  and asserts the response contains "Anders Winnerskjold".

#### [tests/user/test_dictate.py](tests/user/test_dictate.py)

- **`test_user_can_dictate_into_chat_input`** — pipes `tests/fixtures/dictation_sample.wav` into Chrome's fake
  microphone, clicks the voice input button, confirms the recording, and asserts the transcribed text "Hej med dig"
  appears in the chat input. Runs non-headless, so it needs a display (Xvfb in Docker).

#### [tests/user/test_tools.py](tests/user/test_tools.py)

- **`test_user_can_see_available_tools`** — opens the integration menu, opens Værktøjer and asserts websearch,
  eventdatabase, retsinformation, EU founding portal and Office documents are listed.

#### [tests/user/test_upload_menu.py](tests/user/test_upload_menu.py)

- **`test_user_cannot_capture_images`** — opens the upload menu and asserts it has no Capture item and no
  `#camera-input`.

#### [tests/user/test_tts.py](tests/user/test_tts.py)

- **`test_user_can_read_response_aloud`** — sends a prompt, clicks Read Aloud on the response and asserts the
  `/api/v1/audio/speech` request returned 200.

## Exploration

`exploration/explore.py` is a helper for writing new tests: it navigates to a path (optionally logging in first) and
dumps `exploration/explore_screenshot.png` plus `exploration/explore_page.html` so selectors can be inspected without
running a full test. These outputs are not gitignored, so do not commit them. Pass `--click <selector>` (repeatable;
CSS, or XPath if it starts with `//` or `(`) to click elements — e.g. open a menu or flip a toggle — before the capture:

```bash
uv run python exploration/explore.py --login user --click "#integration-menu-button"
```

Via Docker with Task (args after `--`): `task explore -- / --login user --click "#integration-menu-button"`.

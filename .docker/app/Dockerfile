# syntax=docker/dockerfile:1.7

FROM python:3.13-slim-bookworm

# Pull the uv binary from the official image (pin to a release for reproducibility).
COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /uvx /usr/local/bin/

# Chromium + matching chromedriver for Selenium, Xvfb for the non-headless
# dictation test, and fonts so pages/screenshots render properly.
RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        chromium \
        chromium-driver \
        xvfb \
        xauth \
        fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Chrome's sandbox and small default /dev/shm don't work in containers.
# Debian's chromium wrapper sources /etc/chromium.d/*, so these flags apply
# to every browser chromedriver launches — no test-code changes needed.
RUN echo 'export CHROMIUM_FLAGS="$CHROMIUM_FLAGS --no-sandbox --disable-dev-shm-usage"' \
    > /etc/chromium.d/docker-flags

# Place the project venv outside /app so the docker-compose bind-mount of ./:/app
# does not shadow it at runtime.
ENV PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# The project is not a package (no build-system), so a single dependency sync
# from the lockfile is all that's needed.
COPY pyproject.toml uv.lock /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

COPY tests /app/tests
COPY exploration /app/exploration

# Add deploy user to match server.
RUN addgroup --gid 1042 deploy \
    && useradd --gid 1042 --uid 1042 --home-dir /home/deploy --create-home --shell /bin/bash deploy \
    && chown -R deploy:deploy /app /opt/venv

USER deploy

# xvfb-run provides the display the non-headless dictation test needs;
# it is harmless for the headless tests.
ENTRYPOINT ["xvfb-run", "-a"]
CMD ["python", "-m", "unittest"]

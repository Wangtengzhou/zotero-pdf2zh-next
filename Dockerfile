# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm@sha256:392307d22300de8b5986851a12d9176dfc0fc073e65bf6523ebd7dcbeb23564e

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/app \
    HOME=/home/app
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 libxext6 libsm6 libxrender1 libgomp1 build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 app && useradd --uid 10001 --gid app --create-home app

COPY requirements.lock ./
RUN python -m pip install --no-cache-dir --require-hashes -r requirements.lock
COPY versions.json ./
COPY scripts/fetch_upstream.py scripts/fetch_upstream.py
RUN python scripts/fetch_upstream.py /app
RUN mkdir -p /app/gateway/state /app/server/config /app/server/translated /home/app/.cache \
    && chmod 700 /app/gateway/state \
    && chown -R app:app /app/server/config /app/server/translated /app/gateway/state /home/app
USER app
RUN babeldoc --warmup && python -c "import importlib.metadata as m; assert m.version('pdf2zh-next') == '2.9.0'; assert m.version('babeldoc') == '0.6.2'"

USER root
COPY gateway gateway
COPY scripts scripts
COPY THIRD_PARTY_NOTICES.md LICENSE ./
COPY LICENSES LICENSES
RUN install -m 755 scripts/pdf2zh-admin /usr/local/bin/pdf2zh-admin \
    && mkdir -p /app/defaults/config \
    && cp /app/server/config/*.example /app/defaults/config/
USER app
ENV GATEWAY_STATE_DIR=/app/gateway/state

ARG VERSION=0.1.3
ARG SOURCE_URL
ARG REVISION=unknown
LABEL org.opencontainers.image.title="Zotero PDF2zh Next container" \
      org.opencontainers.image.version=$VERSION \
      org.opencontainers.image.source=$SOURCE_URL \
      org.opencontainers.image.revision=$REVISION \
      org.opencontainers.image.licenses="MIT AND AGPL-3.0" \
      io.pdf2zh.server.version="4.1.7" \
      io.pdf2zh.next.version="2.9.0"

EXPOSE 8890
HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
    CMD ["python", "/app/scripts/healthcheck.py"]
CMD ["python", "/app/scripts/supervise.py"]

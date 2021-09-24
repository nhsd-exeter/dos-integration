FROM nhsd/python:latest as base

# ==============================================================================

FROM base as builder

RUN set -eux && \
    # Get Python packages
    mkdir /packages && cd /packages && \
    pip install --upgrade pip && \
    pip install --prefix=/packages --no-warn-script-location --verbose \
        gunicorn==20.1.0

# ==============================================================================

FROM base
ENV \
    APP="" \
    PYTHONPATH="/application"

COPY --from=builder /packages /usr/local
COPY assets/ /

WORKDIR /application
CMD [ "gunicorn" ]
EXPOSE 8443
HEALTHCHECK \
    --start-period=3s \
    --interval=7s \
    --timeout=1s \
    --retries=2 \
    CMD curl --user-agent "healthcheck" --insecure --fail https://localhost:8443/ || exit 1

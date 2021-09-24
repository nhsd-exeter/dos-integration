FROM docker:latest
ENV \
    LANG="C.UTF-8" \
    LC_ALL="C.UTF-8" \
    TZ="UTC"

COPY assets/certificate/certificate.* /certificate/
RUN set -eux && \
    \
    # Get base packages
    apk add --no-cache \
        ca-certificates \
        curl \
        gnupg \
        wget \
        bash \
        git \
        make

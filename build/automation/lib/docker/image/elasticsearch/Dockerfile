FROM bitnami/elasticsearch:latest
ENV \
    DEBIAN_FRONTEND="noninteractive" \
    GOSU_VERSION="1.14" \
    LANG="C.UTF-8" \
    LC_ALL="C.UTF-8" \
    SYSTEM_USER_GID="999" \
    SYSTEM_USER_UID="999" \
    SYSTEM_USER="elasticsearch" \
    TZ="UTC"

USER root
RUN set -eux && \
    \
    # Install base packages
    apt-get update --yes && \
    apt-get install --yes --no-install-recommends \
        ca-certificates \
        curl \
        gnupg \
        wget \
    && \
    \
    # Install gosu
    dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')" && \
    wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch" && \
    wget -O /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch.asc" && \
    export GNUPGHOME="$(mktemp -d)" && \
    gpg --batch --keyserver hkps://keys.openpgp.org --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4 && \
    gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu && \
    gpgconf --kill all && \
    rm -rf "$GNUPGHOME" /usr/local/bin/gosu.asc && \
    chmod +x /usr/local/bin/gosu && \
    gosu nobody true && \
    \
    # Configure system user
    ( userdel --remove --force $SYSTEM_USER ||: ) && \
    groupadd --system --gid $SYSTEM_USER_GID $SYSTEM_USER && \
    useradd --system --create-home --home-dir /tmp --shell=/bin/false --uid $SYSTEM_USER_UID --gid $SYSTEM_USER_GID $SYSTEM_USER && \
    \
    # Clean up
    rm -rf /tmp/* /var/tmp/* /var/lib/apt/lists/* /var/cache/apt/*
COPY assets/ /

WORKDIR /data
ENTRYPOINT [ "/sbin/entrypoint.sh" ]
EXPOSE 9200 9300

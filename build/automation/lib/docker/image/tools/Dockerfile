FROM python:latest as base

# ==============================================================================

FROM base as builder
ENV \
    GOSU_VERSION="1.14"

RUN set -eux && \
    \
    # Get base packages
    apk add --no-cache \
        ca-certificates \
        dpkg \
        gnupg \
        wget \
    && \
    \
    # Get gosu
    dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')" && \
    wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch" && \
    wget -O /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch.asc" && \
    export GNUPGHOME="$(mktemp -d)" && \
    gpg --batch --keyserver hkps://keys.openpgp.org --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4 && \
    gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu && \
    gpgconf --kill all && \
    rm -rf "$GNUPGHOME" /usr/local/bin/gosu.asc && \
    chmod +x /usr/local/bin/gosu

# ==============================================================================

FROM base
ARG PYTHON_BASE_PACKAGES
ENV \
    LANG="C.UTF-8" \
    LC_ALL="C.UTF-8" \
    PYTHONDONTWRITEBYTECODE="1" \
    PYTHONUNBUFFERED="1" \
    SYSTEM_USER_GID="999" \
    SYSTEM_USER_UID="999" \
    SYSTEM_USER="tools" \
    TZ="UTC"

COPY --from=builder /usr/local/bin/gosu /usr/local/bin/gosu
COPY assets/ /
RUN set -eux && \
    \
    # Install base packages
    apk add --no-cache \
        bash \
        bind-tools \
        ca-certificates \
        cmake \
        curl \
        g++ \
        git \
        gnupg \
        graphviz \
        iputils \
        linux-headers \
        make \
        msttcorefonts-installer \
        net-tools \
        netcat-openbsd \
        openssl-dev \
        unzip \
        wget \
        zip \
    && \
    update-ms-fonts && \
    \
    # Get Python packages
    pip install --upgrade pip && \
    pip install --no-warn-script-location \
        $PYTHON_BASE_PACKAGES \
    && \
    \
    # Install aws-iam-authenticator
    curl -o aws-iam-authenticator https://amazon-eks.s3-us-west-2.amazonaws.com/1.21.2/2021-07-05/bin/linux/amd64/aws-iam-authenticator && \
    chmod +x ./aws-iam-authenticator && \
    mv ./aws-iam-authenticator /usr/local/bin/aws-iam-authenticator && \
    \
    # Install ecs-cli
    curl -LO https://amazon-ecs-cli.s3.amazonaws.com/ecs-cli-linux-amd64-v1.21.0 && \
    chmod +x ./ecs-cli-linux-amd64-v1.21.0 && \
    mv ./ecs-cli-linux-amd64-v1.21.0 /usr/local/bin/ecs-cli && \
    \
    # Install jq
    curl -LO https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64 && \
    chmod +x ./jq-linux64 && \
    mv ./jq-linux64 /usr/local/bin/jq && \
    \
    # Install yq
    curl -LO https://github.com/mikefarah/yq/releases/download/v4.20.2/yq_linux_amd64 && \
    chmod +x ./yq_linux_amd64 && \
    mv ./yq_linux_amd64 /usr/local/bin/yq && \
    \
    # Install kubectl
    curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.23.4/bin/linux/amd64/kubectl && \
    chmod +x ./kubectl && \
    mv ./kubectl /usr/local/bin/kubectl && \
    \
    # Configure system user
    ( deluser $SYSTEM_USER ||: ) && ( delgroup $SYSTEM_USER ||: ) && ( delgroup $(getent group $SYSTEM_USER_GID | sed -e "s/:x:$SYSTEM_USER_GID//g") ||: ) && \
    addgroup -S -g $SYSTEM_USER_GID $SYSTEM_USER && \
    adduser -H -D -s /bin/false -g "" -h /tmp -G $SYSTEM_USER -u $SYSTEM_USER_UID $SYSTEM_USER && \
    gosu nobody true

ENTRYPOINT [ "/sbin/entrypoint.sh" ]

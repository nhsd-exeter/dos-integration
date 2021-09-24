FROM nhsd/python-app:VERSION_TEMPLATE_TO_REPLACE as base

FROM base as builder
ADD assets/application.tar.gz /application
RUN set -eux && \
    mkdir /packages && cd /packages && \
    pip install \
        --requirement /application/requirements.txt \
        --prefix=/packages \
        --no-warn-script-location

FROM base
COPY --from=builder /packages /usr/local
COPY assets/certificate /certificate
ADD assets/application.tar.gz /application

FROM nhsd/node:VERSION_TEMPLATE_TO_REPLACE as base

FROM base as builder
COPY example/package.json /package.json
RUN set -eux && \
    cd / && \
    npm install --only=production

FROM base
COPY --from=builder /node_modules /application/node_modules
COPY assets/certificate /certificate
ADD assets/application.tar.gz /application

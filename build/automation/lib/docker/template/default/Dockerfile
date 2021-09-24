FROM nhsd/nginx:latest as base

# ==============================================================================

FROM base

COPY assets/certificate/certificate.* /certificate/
ADD assets/application.tar.gz /application

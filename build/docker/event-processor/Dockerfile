FROM public.ecr.aws/lambda/python:3.9 as base
# Set function directory
ARG FUNCTION_DIR="/var/task"
# ==============================================================================

FROM base as builder
# Install python build dependencies
RUN yum install -y gcc-c++ python-devel postgresql-devel
# Install Python requirements
COPY assets/requirements.txt /
# Install Python requirements
RUN python -m pip install -r /requirements.txt --upgrade --target=${FUNCTION_DIR}

# ======================================================================

FROM base
# Install minimum requirements
RUN yum install -y postgresql
# Copy Python requirements
COPY --from=builder ${FUNCTION_DIR} ${FUNCTION_DIR}
# Copy function code
ADD assets/event-processor-app.tar.gz ${FUNCTION_DIR}
# Set the CMD to your handler
CMD [ "event_processor.lambda_handler" ]

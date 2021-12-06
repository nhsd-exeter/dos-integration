FROM public.ecr.aws/lambda/python:3.9 as base
# Set function directory
# ==============================================================================

FROM base as builder

# Install python build dependencies
RUN yum install -y gcc-c++ python-devel postgresql-devel
# Install Python requirements
COPY assets/requirements.txt /
# Install Python requirements
RUN python -m pip install -r /requirements.txt --upgrade --target="/var/task"

# ======================================================================

FROM base

# Install minimum requirements
RUN yum install -y postgresql

# Copy Python requirements
COPY --from=builder "/var/task" "/var/task"

# Copy function code
ADD assets/event-processor-app.tar.gz "/var/task"
# Set the CMD to your handler
CMD [ "event_processor.lambda_handler" ]

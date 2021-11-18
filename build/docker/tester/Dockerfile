FROM python:latest
# Install python package build requirements
# RUN apk add gcc-c++ libpq-dev python-devel postgresql-devel
RUN apk add postgresql-dev build-base python3-dev musl-dev cmake
# Install Python requirements
COPY assets/requirements.txt /
# Install Python requirements
RUN python -m pip install -r /requirements.txt --upgrade
# Copy function code
# ADD assets/event-processor-app.tar.gz /var/task
# Set the CMD to your handler
# CMD [ "event_processor.lambda_handler" ]

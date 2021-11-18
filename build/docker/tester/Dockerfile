FROM python:latest
# Install python package build requirements
RUN apk add postgresql-dev build-base python3-dev musl-dev cmake
# Copy Full Python requirements
COPY assets/requirements.txt /
# Install Python requirements
RUN python -m pip install -r /requirements.txt --upgrade

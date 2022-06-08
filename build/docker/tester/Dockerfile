FROM python:3.10.5
# Install python package build requirements
RUN apt-get update && apt-get -y install libpq-dev gcc postgresql-client
# Copy Python requirements
COPY assets/requirements.txt /
# Install Python requirements
RUN python -m pip install -r /requirements.txt --upgrade

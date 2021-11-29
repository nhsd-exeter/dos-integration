FROM python:3.9
# Install python package build requirements
RUN apt-get update && apt-get -y install libpq-dev gcc postgresql-client musl-dev
RUN ln -s /usr/lib/x86_64-linux-musl/libc.so /lib/libc.musl-x86_64.so.1
# Install Python requirements
COPY assets/requirements.txt /
# Install Python requirements
RUN python -m pip install -r /requirements.txt --upgrade

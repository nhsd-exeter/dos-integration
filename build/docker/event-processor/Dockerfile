FROM public.ecr.aws/lambda/python:3.9
# Install python package build requirements
RUN yum install -y gcc-c++ libpq-dev python-devel postgresql-devel
# Install Python requirements
COPY assets/requirements.txt /
# Install Python requirements
RUN python -m pip install -r /requirements.txt --upgrade
# Copy function code
ADD assets/event-processor-app.tar.gz /var/task
# Set the CMD to your handler
CMD [ "event_processor.lambda_handler" ]
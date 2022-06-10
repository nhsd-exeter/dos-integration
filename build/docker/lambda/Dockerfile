FROM public.ecr.aws/lambda/python:3.9
# Update all packages
RUN yum update -y
# Copy Python requirements
COPY assets/requirements.txt /
# Install Python requirements
RUN pip install -r /requirements.txt --upgrade
# Copy function code
ADD assets/app.tar.gz "/var/task"
# Set the CMD to your handler
CMD [ "CMD_TO_REPLACE" ]

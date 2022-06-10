FROM public.ecr.aws/lambda/python:3.9
# Copy Python requirements
COPY assets/requirements.txt /
# Install Python requirements
RUN pip install -r /requirements.txt --upgrade
# Copy function code
ADD assets/app.tar.gz "/var/task"
ENV python_entrypoint_file=$python_entrypoint_file
# Set the CMD to your handler
CMD [ "event_sender." ]

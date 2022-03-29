FROM public.ecr.aws/lambda/python:3.9
# Install Python requirements
COPY assets/requirements.txt /
# Install Python requirements
RUN python -m pip install -r /requirements.txt --upgrade --target="/var/task"
# Copy function code
ADD assets/event-processor-app.tar.gz "/var/task"
# Set the CMD to your handler
CMD [ "event_processor.lambda_handler" ]

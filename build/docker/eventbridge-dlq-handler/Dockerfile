FROM public.ecr.aws/lambda/python:3.9
# Copy Python requirements
COPY assets/requirements.txt /
# Install Python requirements
RUN pip install -r /requirements.txt --upgrade
# Copy function code
ADD assets/eventbridge-dlq-handler-app.tar.gz "/var/task"
# Set the CMD to your handler
CMD [ "eventbridge_dlq_handler.lambda_handler" ]

FROM public.ecr.aws/lambda/python:3.9

# Copy function code
ADD assets/event-receiver-app.tar.gz /var/task
# Install Python requirements
RUN pip install -r /var/task/requirements.txt
# Set the CMD to your handler
CMD [ "event_receiver.lambda_handler" ]

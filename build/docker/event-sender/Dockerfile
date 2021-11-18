FROM public.ecr.aws/lambda/python:3.9
# Set function directory
ARG FUNCTION_DIR="/var/task"
# Copy Python requirements
COPY assets/requirements.txt /
# Install Python requirements
RUN pip install -r /requirements.txt --upgrade
# Copy function code
ADD assets/event-sender-app.tar.gz ${FUNCTION_DIR}
# Set the CMD to your handler
CMD [ "event_sender.lambda_handler" ]

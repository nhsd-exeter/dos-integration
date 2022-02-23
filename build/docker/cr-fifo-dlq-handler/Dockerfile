FROM public.ecr.aws/lambda/python:3.9
# Copy Python requirements
COPY assets/requirements.txt /
# Install Python requirements
RUN pip install -r /requirements.txt --upgrade
# Copy function code
ADD assets/cr-fifo-dlq-handler-app.tar.gz "/var/task"
# Set the CMD to your handler
CMD [ "cr_fifo_dlq_handler.lambda_handler" ]

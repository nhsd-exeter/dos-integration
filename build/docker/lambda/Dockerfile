FROM amazon/aws-lambda-python:3.10
# Update all packages
RUN yum update -y
# Add the Lambda Insights Extension
RUN curl -O https://lambda-insights-extension.s3-ap-northeast-1.amazonaws.com/amazon_linux/lambda-insights-extension.rpm && \
    rpm -U lambda-insights-extension.rpm && \
    rm -f lambda-insights-extension.rpm
# Update Pip
RUN python -m pip install --upgrade pip
# Copy Python requirements
COPY assets/requirements.txt /
# Install Python requirements
RUN pip install -r /requirements.txt --upgrade
# Copy function code
ADD assets/app.tar.gz /var/task
# Set the CMD to your handler
CMD [ "CMD_TO_REPLACE" ]

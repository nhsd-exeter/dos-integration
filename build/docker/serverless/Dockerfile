# checkov:skip=CKV_DOCKER_7:Uses NHSD Node Image
FROM node:latest
WORKDIR /
# Install serverless
RUN apk add python3 make gcc g++
RUN export PATH="$PATH:$(yarn global bin)"
RUN yarn global add serverless@3.*
# Install plugins
ADD assets/serverless.tar.gz /deployment/
RUN chmod -R 777 /deployment
WORKDIR /deployment
RUN serverless plugin install -n serverless-vpc-discovery

FROM nhsd/node:latest

# Install serverless
RUN apk add python3 make gcc g++
RUN export PATH="$PATH:$(yarn global bin)"
RUN yarn global add serverless@2.72.2

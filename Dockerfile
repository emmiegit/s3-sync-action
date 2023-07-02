FROM python:3.11-alpine

LABEL "com.github.actions.name"="S3 Sync (charset fix)"
LABEL "com.github.actions.description"="Sync a directory to an AWS S3 repository"
LABEL "com.github.actions.icon"="refresh-cw"
LABEL "com.github.actions.color"="green"

LABEL version="0.1.0"
LABEL repository="https://github.com/emmiegit/s3-sync-action"
LABEL homepage="https://emmie.tech/"
LABEL maintainer="Emmie Maeda <emmie.maeda@gmail.com>"

# Install file/magic utility
RUN apk add --no-cache file

# https://github.com/aws/aws-cli/blob/master/CHANGELOG.rst
ENV AWSCLI_VERSION='1.18.14'
RUN pip install --quiet --no-cache-dir awscli==${AWSCLI_VERSION}

ADD s3_sync.py entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]

FROM python:3.9-slim

# Add a build argument for changed files
ARG CHANGED_FILES

# Set an environment variable for the changed files
ENV CHANGED_FILES=$CHANGED_FILES

# Set the working directory in the container
WORKDIR /app

# Copy local directories with absolute paths
COPY ./submission/ /app/submission/
COPY ./prompts/ /app/prompts/
COPY ./src/ /app/src/

# Copy local files with absolute paths
COPY ./.env /app/.env
COPY ./requirements.txt /app/requirements.txt

# Install AWS CLI and jq in working directory
RUN apt-get update && apt-get install -y python3 jq && pip install awscli

# Install Python dependencies in working directory
RUN pip install -r requirements.txt 

# Give permission to access entrypoint bash script
RUN chmod +x src/entrypoint.sh

ENTRYPOINT [ "src/entrypoint.sh" ]

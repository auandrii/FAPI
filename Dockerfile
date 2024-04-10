# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Giving executable permission
RUN chmod +x run.sh

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Install Playwright
RUN playwright install --with-deps

# Define environment variable
ENV MODULE_NAME=main

CMD ["/bin/sh", "run.sh"]
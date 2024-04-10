# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Install Playwright dependencies (node.js and npm)
# RUN apt-get update && apt-get install -y \
#     npm \
#     && rm -rf /var/lib/apt/lists/*

# Install Playwright
RUN playwright install --with-deps

# Define environment variable
ENV MODULE_NAME=main

# Run main.py when the container launches
#CMD ["playwright", "install"]
CMD ["uvicorn", "main:app", "--host", "127.0.0.1", "--reload"]
# Use an official Python runtime as a parent image
FROM python:3.11.4-alpine3.17

# Set the maintainer label
LABEL maintainer="your-email@example.com"

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN apk update && \
    apk add --no-cache --virtual .build-deps gcc musl-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del .build-deps

# Copy the rest of the application's code
COPY . /app

# Make port 5162 available to the world outside this container
EXPOSE 5162

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "app.py"]

# Use Python 3 as the base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy application files
COPY . /app

# Install required Python packages
RUN pip install -r requirements.txt

# Set the default command to start a Flask server (overridden in docker-compose.yml)
CMD ["python", "backend_server.py"]

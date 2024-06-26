# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the container
COPY . /app/

# Expose the port the app runs on
EXPOSE 8000

# Run the Flask app with Gunicorn
CMD ["gunicorn", "-c", "gunicorn_config.py", "app:app"]

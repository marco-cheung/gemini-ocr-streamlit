# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the application code
COPY . ./

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the application
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
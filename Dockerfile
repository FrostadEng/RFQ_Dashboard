# Use the official Python image as a base image
FROM python:3.12-slim

# Install system dependencies
# - curl is used for the health check
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Create a non-root user and group
RUN useradd -m -u 1000 streamlit

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Change ownership of the app directory to the non-root user
RUN chown -R streamlit:streamlit /app

# Switch to the non-root user
USER streamlit

# Expose the port that Streamlit runs on
EXPOSE 8501

# Health check to ensure the Streamlit server is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health

# Command to run the Streamlit application
CMD ["streamlit", "run", "streamlit_dashboard.py"]
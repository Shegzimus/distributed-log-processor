FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the analyzer code
COPY log_analyzer.py .

# Default command
ENTRYPOINT ["python", "log_analyzer.py"]
CMD ["/logs/generated_logs.log"]

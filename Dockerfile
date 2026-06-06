# Parent image is a lightweight python version
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies like C++ for extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Get my current python libraries installed with pip and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Get main script
COPY ingest_matches.py .

CMD ["python", "ingest_matches.py"]
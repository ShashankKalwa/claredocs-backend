# Use an official lightweight Python image
FROM python:3.11-slim

# Install system-level dependencies (Poppler)
RUN apt-get clean && rm -rf /var/lib/apt/lists/* && \
    apt-get update -o Acquire::CompressionTypes::Order::=gz && \
    apt-get install -y --no-install-recommends poppler-utils && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy files
COPY . .

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Render uses
EXPOSE 10000

# Run the FastAPI app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "10000"]

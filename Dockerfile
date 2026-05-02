FROM python:3.12-slim

WORKDIR /app

# Install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Create data directory for SQLite (if used)
RUN mkdir -p /app/data

# Make start script executable
RUN chmod +x start.sh

# Expose default port
EXPOSE 8000

# Run via bash script (proper env var expansion)
CMD ["bash", "start.sh"]

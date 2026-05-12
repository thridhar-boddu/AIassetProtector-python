FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY main.py .

# Render injects PORT automatically; main.py reads it
EXPOSE 8080

CMD ["python", "main.py"]

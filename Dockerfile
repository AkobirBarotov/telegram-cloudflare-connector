FROM python:3.11-slim

# Set workdir to project src
WORKDIR /app

# Copy requirements first for caching
COPY container_src/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY container_src/src . 

EXPOSE 8080

CMD ["python3", "main.py"]

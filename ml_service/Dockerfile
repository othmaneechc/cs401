# Use a lightweight Python base image
FROM python:3.9-slim-bullseye
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the ML code into the container
COPY . .

# Run the ML rule generation script when the container starts
CMD ["python", "ml_rules.py"]

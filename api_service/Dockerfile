FROM python:3.9-slim-bullseye
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the API code into the container
COPY . .

# Set the environment variable so Flask knows where to find the app
ENV FLASK_APP=app

# Run the Flask app on port 5000
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
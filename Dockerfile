# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Expose port for flask
EXPOSE 5000

# default command runs the flask app (so CI can hit endpoints)
CMD ["python", "email_automation.py"]


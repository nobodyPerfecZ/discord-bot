FROM python:3.10

WORKDIR /app

# Install system dependencies
RUN apt-get update 
RUN apt-get install -y ffmpeg

# Copy requirements file and install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app

CMD ["python", "main.py"]

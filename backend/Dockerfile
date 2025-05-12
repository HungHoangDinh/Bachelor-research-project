FROM python:3.10

# Cài đặt các gói cần thiết
RUN apt update && apt-get install -y ffmpeg poppler-utils &&\
    apt clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

EXPOSE 8000

CMD ["python", "src/app.py"]
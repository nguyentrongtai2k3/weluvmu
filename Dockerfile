FROM python:3.10-slim

# Cài wget và cài trực tiếp file .deb của Google Chrome (Bypass lỗi apt-key)
RUN apt-get update && apt-get install -y wget gnupg unzip \
    && wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py .

# Khai báo mở port 10000
EXPOSE 10000

CMD ["python", "-u", "bot.py"]
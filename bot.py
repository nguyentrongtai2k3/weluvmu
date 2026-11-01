import requests
import random
import time
import threading
import datetime
import uuid  # Thêm thư viện tạo mã định danh ngẫu nhiên
from flask import Flask

# Mày tự copy URL trong tab "Headers -> Request URL" dán vào đây nhé
API_URL = "https://weluvunited.com/api/actions"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://weluvunited.com",
    "Referer": "https://weluvunited.com/glazers-out?ref=trongtai"
}

app = Flask(__name__)


@app.route('/')
def keep_alive():
    return "Bot API đang chạy!"


def get_dynamic_delay():
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    vn_time = utc_now + datetime.timedelta(hours=7)
    hour = vn_time.hour

    if 0 <= hour < 6:
        return random.uniform(30, 60)
    elif 11 <= hour < 14 or 19 <= hour < 24:
        return random.uniform(15, 30)
    else:
        return random.uniform(5, 20)


def perform_api_call():
    try:
        # Tự động sinh chuỗi mã hóa 32 ký tự giống hệt định dạng của web
        fake_token = uuid.uuid4().hex

        # Nhét token ảo, actionNumber 2 và choice "yes" vào cấu trúc Payload
        PAYLOAD = {
            "visitorToken": fake_token,
            "actionNumber": 2,
            "choice": "yes"
        }

        response = requests.post(API_URL, json=PAYLOAD, headers=HEADERS, timeout=10)

        if response.status_code in [200, 201]:
            print(f"[+] Thành công! (Fake Token: {fake_token[:8]}...)")
        else:
            print(f"[-] Lỗi {response.status_code}: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"[-] Lỗi mạng: {e}")


def run_bot_forever():
    print("🚀 Worker API-Request (RAM 0MB) Khởi động...")
    count = 1
    while True:
        print(f"\n--- Lượt {count} ---")
        perform_api_call()

        count += 1
        delay = get_dynamic_delay()

        utc_now = datetime.datetime.now(datetime.timezone.utc)
        vn_time = utc_now + datetime.timedelta(hours=7)
        print(f"[*] [Khung giờ: {vn_time.strftime('%H:%M')}] Chờ {delay:.2f}s...")
        time.sleep(delay)


if __name__ == "__main__":
    threading.Thread(target=run_bot_forever, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
import random
import time
import threading
import datetime
import gc
import os
from flask import Flask
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TARGET_URL = "https://weluvunited.com/glazers-out?ref=trongtai"
BUTTON_ID = "btn-yes-i-will"
LET_DO_THIS_XPATH = "/html/body/div[1]/div/div/div[2]/button[2]"

app = Flask(__name__)


@app.route('/')
def keep_alive():
    return "Render thấy web đang sống, còn Bot thì đang chạy ngầm ở tốc độ tối đa!"


def get_dynamic_delay():
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    vn_time = utc_now + datetime.timedelta(hours=7)
    hour = vn_time.hour

    # Phân bổ ~650 traffic/ngày (Ép xung tối đa)
    if 0 <= hour < 6:
        # Đêm (Gánh ~70 clicks): 3 - 7 phút/lần
        return random.uniform(180, 420)
    elif 6 <= hour < 11:
        # Sáng (Gánh ~130 clicks): 1.5 - 3 phút/lần
        return random.uniform(90, 180)
    elif 11 <= hour < 14:
        # Trưa Peak 1 (Gánh ~120 clicks): 60s - 120s/lần
        return random.uniform(60, 120)
    elif 14 <= hour < 19:
        # Chiều (Gánh ~130 clicks): 1.5 - 3 phút/lần
        return random.uniform(90, 180)
    else:
        # Tối Peak 2 (Gánh ~200 clicks): 45s - 120s/lần
        return random.uniform(45, 120)


def force_kill_chrome():
    try:
        os.system("killall -9 chrome chromedriver 2>/dev/null")
    except:
        pass


def perform_click():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--incognito")

    # Cấu hình tối ưu RAM (Bắt buộc giữ cho tần suất cao)
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-default-apps")
    options.add_argument("--mute-audio")
    options.add_argument("--no-zygote")
    options.add_argument('--blink-settings=imagesEnabled=false')

    # Flag ngụy trang Anti-bot
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)
    try:
        print(f"[*] Đang mở trang (Chế độ Max Speed)...")
        driver.get(TARGET_URL)
        wait = WebDriverWait(driver, 15)

        button_yes_iwill = wait.until(EC.presence_of_element_located((By.ID, BUTTON_ID)))
        driver.execute_script("arguments[0].click();", button_yes_iwill)
        print("[+] Đã click 'Yes I will'")
        time.sleep(1)

        button_let_do_this = wait.until(EC.presence_of_element_located((By.XPATH, LET_DO_THIS_XPATH)))
        driver.execute_script("arguments[0].click();", button_let_do_this)
        print("[+] Đã click 'LET'S DO THIS!'")
        time.sleep(1.5)

        num_sponsors = random.randint(1, 12)
        print(f"[*] Sẽ chọn ngẫu nhiên {num_sponsors} sponsors...")
        sponsor_indices = random.sample(range(1, 13), num_sponsors)

        for index in sponsor_indices:
            sponsor_xpath = f"/html/body/div[1]/div/main/section[2]/div/div[1]/div/div[2]/div/div[1]/button[{index}]"
            try:
                sponsor_btn = wait.until(EC.presence_of_element_located((By.XPATH, sponsor_xpath)))
                driver.execute_script("arguments[0].click();", sponsor_btn)
                print(f"  -> Đã click sponsor ở vị trí x = {index}")
                time.sleep(random.uniform(0.3, 0.8))  # Giảm thời gian chờ giữa các lần click Sponsor xuống
            except:
                pass

        print(f"[+] Đã chọn {num_sponsors} sponsors. Hoàn thành!")

    except Exception as e:
        print(f"[-] Lỗi lượt chạy: {e}")
    finally:
        driver.quit()


def run_bot_forever():
    print("🚀 Worker Max Speed (~650 Clicks/Ngày) Khởi động...")
    count = 1
    while True:
        print(f"\n--- Lượt {count} ---")
        perform_click()

        force_kill_chrome()
        gc.collect()

        count += 1
        delay = get_dynamic_delay()

        utc_now = datetime.datetime.now(datetime.timezone.utc)
        vn_time = utc_now + datetime.timedelta(hours=7)
        print(f"[*] [Khung giờ: {vn_time.strftime('%H:%M')}] Dọn RAM xong! Chờ {delay:.2f}s trước khi mở lại...")
        time.sleep(delay)


if __name__ == "__main__":
    threading.Thread(target=run_bot_forever, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
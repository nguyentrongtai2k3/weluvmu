import datetime
import gc
import os
import time
import random
import threading
from flask import Flask
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Cấu hình
TARGET_URL = "https://weluvunited.com/ads?ref=trongtai&lang=vi"
BUTTON_ID = "btn-yes-i-will"

# Khởi tạo Web Server giả
app = Flask(__name__)


@app.route('/')
def keep_alive():
    return "Render thấy web sống, còn Bot Selenium thì đang cày ngầm (Mở/Đóng mỗi lượt)!"


def get_dynamic_delay():
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    vn_time = utc_now + datetime.timedelta(hours=7)
    hour = vn_time.hour

    # Mục tiêu: ~284 clicks/ngày/máy -> 3 máy sẽ đạt ~852 clicks/ngày
    # 22 ngày * 852 = ~18,744 clicks + 300 (vốn) = ~19,044 clicks.

    if 0 <= hour < 6:
        # Đêm khuya: Trung bình 25 phút/lượt. (Gánh ~14 clicks)
        return random.uniform(1200, 1800)

    elif 11 <= hour < 14 or 19 <= hour < 24:
        # Giờ cao điểm (Trưa & Tối): Trung bình ~3 phút/lượt. (Gánh ~164 clicks)
        return random.uniform(130, 220)

    else:
        # Giờ hành chính (Sáng & Chiều): Trung bình ~5.5 phút/lượt. (Gánh ~106 clicks)
        return random.uniform(240, 440)

def force_kill_chrome():
    try:
        if os.name == 'nt':
            os.system("taskkill /f /im chrome.exe >nul 2>&1")
            os.system("taskkill /f /im chromedriver.exe >nul 2>&1")
        else:
            os.system("killall -9 chrome chromedriver 2>/dev/null")
    except:
        pass


def perform_click():
    """Khởi tạo, thao tác và đóng hẳn trình duyệt trong cùng 1 lượt"""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Đổi về headless cơ bản cho Linux
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--incognito")

    options.add_argument("--disable-extensions")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-default-apps")
    options.add_argument("--mute-audio")
    # Xóa cờ --no-zygote để tránh lỗi Chrome instance exited trên VPS
    options.add_argument('--blink-settings=imagesEnabled=false')

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = None  # Khai báo biến trước
    try:
        # BỌC LỆNH MỞ CHROME VÀO ĐÂY. Nếu lỗi, vòng lặp ngoài sẽ bỏ qua và thử lại lượt sau.
        driver = webdriver.Chrome(options=options)

        driver.get(TARGET_URL)
        wait = WebDriverWait(driver, 15)

        # Chờ, cuộn trang và click
        button_yes_iwill = wait.until(EC.element_to_be_clickable((By.ID, BUTTON_ID)))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button_yes_iwill)
        time.sleep(0.5)

        driver.execute_script("arguments[0].click();", button_yes_iwill)
        print("[+] Đã click 'Yes I will'. Cắt bỏ hoàn toàn Sponsor!")

        time.sleep(1)

    except Exception as e:
        print(f"[-] Lỗi lượt chạy (Đã bắt lỗi, Bot vẫn sẽ chạy tiếp): {e}")
    finally:
        # Chắc chắn đóng Chrome ở cuối lượt dù có lỗi hay không
        if driver is not None:
            try:
                driver.quit()
            except:
                pass


def run_bot_forever():
    """Hàm chạy ngầm vòng lặp vô tận của Bot"""
    print("🚀 Bắt đầu tool auto-click (Cơ chế Đóng/Mở liên tục). Bấm Ctrl+C để dừng.")

    force_kill_chrome()
    count = 1

    try:
        while True:
            print(f"--- Vòng lặp thứ {count} ---")

            # Gọi hàm click
            perform_click()

            delay = get_dynamic_delay()
            print(f"[*] Chờ {delay:.2f}s trước khi mở cửa sổ mới...")

            # Dọn RAM định kỳ mỗi 10 lượt
            if count % 50 == 0:
                force_kill_chrome()
                print("[*] Dọn RAM xong!")
                gc.collect()

            count += 1
            time.sleep(delay)

    except KeyboardInterrupt:
        print("\n🛑 Đã dừng tool theo yêu cầu (Ctrl+C).")
    finally:
        force_kill_chrome()


if __name__ == "__main__":
    # 1. Bật bot Selenium chạy ở một luồng riêng biệt
    bot_thread = threading.Thread(target=run_bot_forever, daemon=True)
    bot_thread.start()

    # 2. Bật Web Server giả ở luồng chính để qua mặt bài test Timed Out của Render
    app.run(host='0.0.0.0', port=10000)
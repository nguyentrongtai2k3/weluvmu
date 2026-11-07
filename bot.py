import time
import random
import threading
from flask import Flask
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# Cấu hình
TARGET_URL = "https://weluvunited.com/glazers-out?ref=trongtai"
BUTTON_ID = "btn-yes-i-will"

# Khởi tạo Web Server giả
app = Flask(__name__)


@app.route('/')
def keep_alive():
    return "Render thấy web sống, còn Bot Selenium thì đang cày ngầm!"


def perform_click():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--incognito")

    options.add_argument("--disable-extensions")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-default-apps")
    options.add_argument("--mute-audio")
    options.add_argument("--no-zygote")
    options.add_argument('--blink-settings=imagesEnabled=false')

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(TARGET_URL)
        wait = WebDriverWait(driver, 15)  # Nới lên 15s cho an toàn

        # SỬA LỖI 1: Chờ đến khi nút thực sự ở trạng thái "có thể click"
        button_yes_iwill = wait.until(EC.element_to_be_clickable((By.ID, BUTTON_ID)))

        # SỬA LỖI 2: Cuộn màn hình để ép cái nút ra chính giữa, né các thanh menu bị ghim ở đỉnh/đáy màn hình
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button_yes_iwill)
        time.sleep(0.5)  # Đợi một nhịp cực ngắn để hiệu ứng cuộn dừng hẳn

        # SỬA LỖI 3: Dùng JS ép click xuyên qua mọi layer vô hình đang đè lên
        driver.execute_script("arguments[0].click();", button_yes_iwill)
        print("[+] Đã click 'Yes I will'. Cắt bỏ hoàn toàn Sponsor!")

        time.sleep(1)

    except Exception as e:
        print(f"[-] Lỗi lượt chạy: {e}")
    finally:
        driver.quit()


def run_bot_forever():
    """Hàm chạy ngầm vòng lặp vô tận của Bot"""
    print("🚀 Bắt đầu tool auto-click chạy ngầm. Bấm Ctrl+C để dừng.")
    count = 1
    try:
        while True:
            print(f"--- Vòng lặp thứ {count} ---")
            perform_click()
            count += 1

            # Delay ngẫu nhiên giữa các lần mở trình duyệt để tránh bị ban IP quá nhanh
            delay = random.uniform(2, 5)
            print(f"[*] Chờ {delay:.2f}s trước khi mở cửa sổ mới...")
            time.sleep(delay)

    except KeyboardInterrupt:
        print("\n🛑 Đã dừng tool theo yêu cầu (Ctrl+C).")


if __name__ == "__main__":
    # 1. Bật bot Selenium chạy ở một luồng riêng biệt (Daemon Thread)
    bot_thread = threading.Thread(target=run_bot_forever, daemon=True)
    bot_thread.start()

    # 2. Bật Web Server giả ở luồng chính để Render kiểm tra qua môn
    app.run(host='0.0.0.0', port=10000)
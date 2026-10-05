import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TARGET_URL = "https://weluvunited.com/glazers-out?ref=trongtai"
BUTTON_ID = "btn-yes-i-will"


def perform_click():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--incognito")

    driver = webdriver.Chrome(options=options)
    try:
        print(f"[*] Đang mở trang: {TARGET_URL}")
        driver.get(TARGET_URL)
        wait = WebDriverWait(driver, 15)
        button = wait.until(EC.presence_of_element_located((By.ID, BUTTON_ID)))
        driver.execute_script("arguments[0].click();", button)
        print("[+] Click thành công!")
    except Exception as e:
        print(f"[-] Lỗi: {e}")
    finally:
        driver.quit()
        print("[*] Dọn dẹp RAM xong.")


if __name__ == "__main__":
    print("🚀 Khởi động Worker Auto Click...")
    count = 1
    while True:
        print(f"\n--- Lượt {count} ---")
        perform_click()
        count += 1

        # Ngủ 2 phút (120 giây) trước khi chạy vòng mới
        delay = 120
        print(f"[*] Ngủ {delay}s chờ vòng tiếp theo...")
        time.sleep(delay)
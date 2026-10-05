# bot.py
import time
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
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # Khởi tạo driver (GitHub Actions ubuntu-latest đã có sẵn Chrome)
    driver = webdriver.Chrome(options=options)

    try:
        print(f"[*] Đang mở trang: {TARGET_URL}")
        driver.get(TARGET_URL)

        # Đợi DOM load
        wait = WebDriverWait(driver, 15)
        button = wait.until(EC.presence_of_element_located((By.ID, BUTTON_ID)))

        # Click bằng Javascript
        driver.execute_script("arguments[0].click();", button)
        print("[+] Click thành công trên GitHub Actions!")

        # Ngủ 2s để trình duyệt kịp gửi request về server web trước khi bị kill
        time.sleep(2)

    except Exception as e:
        print(f"[-] Lỗi: {e}")
    finally:
        driver.quit()
        print("[*] Hoàn thành job.")


if __name__ == "__main__":
    perform_click()
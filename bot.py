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
LET_DO_IT_XPATH = "/html/body/div[2]/div/div/div[2]/button[2]"
SPONSOR_XPATH = "/html/body/div[2]/div/main/section[2]/div/div[1]/div/div[2]/div/div[1]/button[1]"
DONE_BTN_XPATH = "/html/body/div[2]/div/main/section[2]/div/div[1]/div/div[2]/div/div[2]/button"
FINAL_BTN_XPATH = "/html/body/div[2]/div/main/section[2]/div/div[1]/div/div[3]/div[2]/div/button"

# Khởi tạo Web Server giả
app = Flask(__name__)


@app.route('/')
def keep_alive():
    return "Render thấy web sống, còn Bot Selenium thì đang cày ngầm (Mở/Đóng mỗi lượt)!"


def get_dynamic_delay():
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    vn_time = utc_now + datetime.timedelta(hours=7)
    hour = vn_time.hour

    # Mục tiêu: ~285 clicks/ngày/máy -> 3 máy sẽ đạt ~855 clicks/ngày
    # Đã trừ hao ~60 giây thời gian bot chạy thực tế.

    if 0 <= hour < 6:
        # Đêm khuya: Chờ ngẫu nhiên 10 - 12 phút/lượt.
        # Sinh ra khoảng ~15 clicks
        return random.uniform(600, 750)

    elif 11 <= hour < 14 or 19 <= hour < 24:
        # Giờ cao điểm (Trưa & Tối): Chờ ngẫu nhiên 1.5 - 2.8 phút/lượt.
        # Sinh ra khoảng ~150 clicks
        return random.uniform(40, 70)

    else:
        # Giờ hành chính (Sáng & Chiều): Chờ ngẫu nhiên 3 - 5 phút/lượt.
        # Sinh ra khoảng ~120 clicks
        return random.uniform(70, 120)

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

        # ========================================================
        # 1. (RANDOM SCROLL)
        # ========================================================
        time.sleep(random.uniform(1.5, 3.0))
        total_height = driver.execute_script("return document.body.scrollHeight")
        viewport_height = driver.execute_script("return window.innerHeight")

        if total_height > viewport_height:
            scroll_steps = random.randint(1, 20)
            print(f"[*] Đang giả lập lướt web (Cuộn ngẫu nhiên {scroll_steps} nhịp để qua mặt GA)...")
            for _ in range(scroll_steps):
                random_y = random.randint(100, total_height - viewport_height)
                driver.execute_script(f"window.scrollTo({{top: {random_y}, behavior: 'smooth'}});")
                time.sleep(random.uniform(1.0, 4.0))
        # ========================================================

        # ========================================================
        # 3. CLICK NÚT CHÍNH "YES I WILL"
        # ========================================================
        wait = WebDriverWait(driver, 15)
        button_yes_iwill = wait.until(EC.element_to_be_clickable((By.ID, BUTTON_ID)))

        driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", button_yes_iwill)
        time.sleep(random.uniform(0.8, 1.5))

        driver.execute_script("arguments[0].click();", button_yes_iwill)
        print("[+] Đã click 'Yes I will'.")

        wait = WebDriverWait(driver, 15)
        button_let_do_it = wait.until(EC.element_to_be_clickable((By.XPATH, LET_DO_IT_XPATH)))
        driver.execute_script("arguments[0].click();", button_let_do_it)
        time.sleep(random.uniform(1.5, 3.8))
        print("[+] Đã click 'Let's do this!")
        # ========================================================
        # 2. CLICK SPONSOR NGẪU NHIÊN (TỪ 1 ĐẾN 12)
        # ========================================================
        try:
            # Random số lượng sponsor muốn click trong lượt này (ví dụ random từ 1 đến 5 để đỡ tốn thời gian, hoặc 1 đến 12 tùy ý)
            # Ở đây tôi set từ 1 đến 6 để giữ tốc độ chạy bot hợp lý, bạn có thể chỉnh lại thành (1, 12) nếu muốn cày mạnh
            num_sponsors_to_click = random.randint(1, 6)

            # Lấy ngẫu nhiên các vị trí button (không trùng lặp)
            sponsor_indices = random.sample(range(1, 13), num_sponsors_to_click)
            print(f"[*] Mục tiêu: Click {num_sponsors_to_click} sponsor ở các vị trí {sponsor_indices}")

            for idx in sponsor_indices:
                # Gắn index động vào XPath
                dynamic_xpath = f"/html/body/div[2]/div/main/section[2]/div/div[1]/div/div[2]/div/div[1]/button[{idx}]"

                try:
                    # Chờ 5s cho mỗi sponsor, không thấy thì bỏ qua nhanh để bấm cái khác
                    wait_sponsor = WebDriverWait(driver, 5)
                    sponsor_el = wait_sponsor.until(EC.element_to_be_clickable((By.XPATH, dynamic_xpath)))

                    # Cuộn tới Sponsor đó và click
                    # driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
                    #                       sponsor_el)
                    time.sleep(random.uniform(0.5, 1.2))  # Nghỉ một nhịp trước khi bấm
                    driver.execute_script("arguments[0].click();", sponsor_el)
                    print(f"[+] Đã click Sponsor số {idx}!")

                    # Nghỉ ngẫu nhiên để mô phỏng tương tác
                    time.sleep(random.uniform(1.5, 3.5))

                    # Xử lý trường hợp bấm Sponsor bị nhảy sang tab mới
                    if len(driver.window_handles) > 1:
                        driver.switch_to.window(driver.window_handles[0])
                        print("[*] Đã quay lại tab chính.")

                except Exception:
                    print(f"[-] Bỏ qua Sponsor số {idx} (Không tìm thấy hoặc không click được).")
            time.sleep(random.uniform(0.5, 2.4))
            wait = WebDriverWait(driver, 15)
            done_btn = wait.until(EC.element_to_be_clickable((By.XPATH, DONE_BTN_XPATH)))
            driver.execute_script("arguments[0].click();", done_btn)
            time.sleep(random.uniform(0.5, 2.4))
            wait = WebDriverWait(driver, 15)
            if random.randint(0, 1) == 1:
                final_btn = wait.until(EC.element_to_be_clickable((By.XPATH, FINAL_BTN_XPATH)))
                driver.execute_script("arguments[0].click();", done_btn)
            print("[+] Đã click 'Done!. Hoàn thành luồng !")
        except Exception as e:
            print(f"[-] Lỗi trong quá trình click sponsor: {e}")


        time.sleep(random.uniform(1.0, 2.0))

    except Exception as e:
        print(f"[-] Lỗi lượt chạy: {e}")
    finally:
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

            delay = random.uniform(10, 20)
            print(f"[*] Chờ {delay:.2f}s trước khi mở cửa sổ mới...")

            # Dọn RAM định kỳ mỗi 50 lượt
            if count % 50 == 0 and count != 0:
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
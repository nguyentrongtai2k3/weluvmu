import datetime
import random
import time
import threading
from flask import Flask
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TARGET_URL = "https://weluvunited.com/glazers-out?ref=trongtai"
BUTTON_ID = "btn-yes-i-will"
LET_DO_THIS_XPATH="/html/body/div[1]/div/div/div[2]/button[2]"

app = Flask(__name__)


# Web server giả để lừa Render
@app.route('/')
def keep_alive():
    return "Render thấy web đang sống, còn Bot thì đang chạy ngầm!"


def get_dynamic_delay():
    # Lấy giờ hiện tại theo múi giờ Việt Nam (UTC+7)
    utc_now = datetime.datetime.utcnow()
    vn_time = utc_now + datetime.timedelta(hours=7)
    hour = vn_time.hour

    # Phân bổ 60-70 traffic/ngày theo hành vi sinh hoạt
    if 0 <= hour < 6:
        # Đêm khuya: 50 - 100 phút/lần
        return random.uniform(3000, 6000)
    elif 6 <= hour < 11:
        # Sáng: 15 - 35 phút/lần
        return random.uniform(900, 2100)
    elif 11 <= hour < 14:
        # Nghỉ trưa: 6 - 16 phút/lần
        return random.uniform(400, 1000)
    elif 14 <= hour < 19:
        # Chiều: 15 - 30 phút/lần
        return random.uniform(900, 1800)
    else:
        # Tối (Giờ vàng): 10 - 20 phút/lần
        return random.uniform(600, 1200)

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
        button_yes_iwill = wait.until(EC.presence_of_element_located((By.ID, BUTTON_ID)))
        button_let_do_this = wait.until(EC.presence_of_element_located((By.XPATH, LET_DO_THIS_XPATH)))

        # BƯỚC 1: Click Yes I Will
        driver.execute_script("arguments[0].click();", button_yes_iwill)
        print("[+] Đã click nút 'Yes I will'!")
        time.sleep(1)

        # BƯỚC 2: Random click let do this
        driver.execute_script("arguments[0].click();", button_let_do_this)
        print("[+] Đã click nút 'LET'S DO THIS!' trên popup!")
        time.sleep(1)

        # BƯỚC 3: Random click Sponsor
        num_sponsors = random.randint(1, 12)
        print(f"[*] Sẽ chọn ngẫu nhiên {num_sponsors} sponsors...")
        time.sleep(1)

        # random.sample giúp lấy ra N số ngẫu nhiên KHÔNG TRÙNG LẶP từ 1 đến 12
        sponsor_indices = random.sample(range(1, 13), num_sponsors)

        for index in sponsor_indices:
            # Gắn biến x vào XPath
            sponsor_xpath = f"/html/body/div[1]/div/main/section[2]/div/div[1]/div/div[2]/div/div[1]/button[{index}]"
            try:
                sponsor_btn = wait.until(EC.presence_of_element_located((By.XPATH, sponsor_xpath)))
                driver.execute_script("arguments[0].click();", sponsor_btn)
                print(f"  -> Đã click sponsor ở vị trí x = {index}")

                # Delay ngẫu nhiên 0.5 - 1.5s giữa các lần chọn để giống người thật
                time.sleep(random.uniform(0.5, 1.5))
            except Exception as ex:
                print(f"  -> Bỏ qua vị trí {index} vì chưa tìm thấy nút (Lỗi phụ)")

        print("[+] Hoàn thành toàn bộ luồng click cho lượt này!")

    except Exception as e:
        print(f"[-] Lỗi: {e}")
    finally:
        driver.quit()


def run_bot_forever():
    print("🚀 Khởi động Worker Auto Click...")
    count = 1
    while True:
        print(f"\n--- Lượt {count} ---")
        perform_click()
        count += 1
        # Lấy delay động theo khung giờ sinh học
        delay = get_dynamic_delay()

        # In thêm khung giờ hiện tại ra Log để dễ theo dõi
        utc_now = datetime.datetime.utcnow()
        vn_time = utc_now + datetime.timedelta(hours=7)
        print(f"[*] [Khung giờ: {vn_time.strftime('%H:%M')}] Chờ {delay:.2f}s trước khi mở cửa sổ mới...")
        time.sleep(delay)


if __name__ == "__main__":
    # Tách luồng: Bot chạy một đường, Web chạy một đường
    threading.Thread(target=run_bot_forever, daemon=True).start()

    # Mở port 10000 cho Render
    app.run(host='0.0.0.0', port=10000)
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

from config import ACCOUNT, PASSWORD, PROXY_STR, CHROME_DRIVER_PATH

chrome_options = Options()
# 设置代理
chrome_options.add_argument(f'--proxy-server={PROXY_STR}')
# 最大化窗口
chrome_options.add_argument('--start-maximized')
# 禁用 GPU 加速
chrome_options.add_argument("--disable-gpu")
# 绕过操作系统安全模型
chrome_options.add_argument("--no-sandbox")
# 解决资源限制问题
chrome_options.add_argument("--disable-dev-shm-usage")
# 设置无头模式
chrome_options.add_argument('--headless')


# Linux 设置chomedriver路径
if os.name != 'nt':
    # 创建 Service 对象
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
# Windows 设置
else:
    driver = webdriver.Chrome(options=chrome_options)


def muniu_sign():
    print('正在打开muniu网站')
    driver.get('https://muniucloud.quest/')
    print('正在登录')
    # 登录
    email_input = WebDriverWait(driver, 100).until(
        EC.visibility_of_element_located((By.ID, "email"))
    )
    passwd_input = WebDriverWait(driver, 100).until(
        EC.visibility_of_element_located((By.ID, "password"))
    )
    login_btn = WebDriverWait(driver, 100).until(
        EC.visibility_of_element_located((By.ID, "login_submit"))
    )
    email_input.send_keys(ACCOUNT)
    passwd_input.send_keys(PASSWORD)
    login_btn.click()
    print('登录成功')

    try:
        print('正在检查签到状态')
        wait = WebDriverWait(driver, 2)  # 等待2秒
        # element = driver.find_elements(By.CSS_SELECTOR, '.btn.btn-transparent-white.font-weight-bold.py-3.px-6.mr-2.disabled')
        element = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '.btn.btn-transparent-white.font-weight-bold.py-3.px-6.mr-2.disabled')))
        print(element)
        if element:
            print("今日已签到")
        else:
            raise Exception
    except:
        print("今日未签到")
        # 签到
        sign_in_btn = WebDriverWait(driver, 100).until(
            EC.visibility_of_element_located((By.ID, "checkin"))
        )
        print("正在签到")
        sign_in_btn.click()
        time.sleep(2)
        print("签到成功")


if __name__ == '__main__':
    muniu_sign()
    driver.close()
    driver.quit()

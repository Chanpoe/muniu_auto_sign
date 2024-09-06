from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import ACCOUNT, PASSWORD, PROXY_STR

chrome_options = Options()
# 设置代理
chrome_options.add_argument(f'--proxy-server={PROXY_STR}')
# 最大化窗口
chrome_options.add_argument('--start-maximized')
# 设置无头模式
chrome_options.add_argument('--headless')
chrome_options.add_argument("--disable-gpu")  # 禁用 GPU 加速
chrome_options.add_argument("--no-sandbox")  # 绕过操作系统安全模型
chrome_options.add_argument("--disable-dev-shm-usage")  # 解决资源限制问题
chrome_options.add_argument("--user-data-dir=/tmp/chrome-user-data")  # 自定义用户数据目录

# driver = webdriver.Chrome(executable_path='/root/pythonfiles/chromedriver', options=chrome_options)
driver = webdriver.Chrome(options=chrome_options)


def muniu_sign():
    driver.get('https://muniucloud.quest/')

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

    try:
        if EC.visibility_of_element_located(
                (By.CLASS_NAME, "btn btn-transparent-white font-weight-bold py-3 px-6 mr-2 disabled")):
            print("今日已签到")
    except:
        # 签到
        sign_in_btn = WebDriverWait(driver, 100).until(
            EC.visibility_of_element_located((By.ID, "checkin"))
        )
        sign_in_btn.click()


if __name__ == '__main__':
    muniu_sign()
    driver.close()
    driver.quit()

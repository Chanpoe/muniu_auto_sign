import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.keys import Keys

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
if os.name != 'nt':
    # 设置无头模式
    chrome_options.add_argument('--headless')
# 忽略证书错误（给代理/握手偶发失败兜底）
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.set_capability('acceptInsecureCerts', True)
# 关闭密码管理器与提示弹窗
chrome_options.add_experimental_option('prefs', {
    'credentials_enable_service': False,
    'profile.password_manager_enabled': False,
})
chrome_options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
chrome_options.add_argument('--disable-notifications')


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

    def wait_document_ready(max_wait: int = 30):
        WebDriverWait(driver, max_wait).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )

    def safe_click(element, desc: str = '', retries: int = 3, wait_clickable: int = 15):
        last_err = None
        for attempt in range(1, retries + 1):
            try:
                # 等待元素处于可见且可用的状态
                WebDriverWait(driver, wait_clickable).until(
                    lambda d: element.is_displayed() and element.is_enabled()
                )
                # 滚动到可见
                driver.execute_script('arguments[0].scrollIntoView({block: "center"});', element)
                time.sleep(0.15)
                try:
                    element.click()
                    return True
                except (ElementClickInterceptedException, WebDriverException):
                    # 使用 ActionChains 尝试
                    try:
                        ActionChains(driver).move_to_element(element).pause(0.05).click().perform()
                        return True
                    except (ElementClickInterceptedException, WebDriverException):
                        # JS 回退点击
                        try:
                            driver.execute_script('arguments[0].click();', element)
                            return True
                        except Exception:
                            # 派发 MouseEvent 触发器
                            driver.execute_script(
                                "var e1=new MouseEvent('mousedown',{bubbles:true,cancelable:true,view:window});"
                                "var e2=new MouseEvent('mouseup',{bubbles:true,cancelable:true,view:window});"
                                "var e3=new MouseEvent('click',{bubbles:true,cancelable:true,view:window});"
                                "arguments[0].dispatchEvent(e1);arguments[0].dispatchEvent(e2);arguments[0].dispatchEvent(e3);",
                                element
                            )
                            return True
            except (StaleElementReferenceException, TimeoutException, WebDriverException) as e:
                last_err = e
                time.sleep(0.3)
        if last_err:
            raise last_err
        return False

    def wait_until_any(conditions, timeout: int = 30):
        return WebDriverWait(driver, timeout).until(lambda d: any(
            bool(cond(d)) for cond in conditions
        ))

    def try_dismiss_site_dialogs(max_rounds: int = 3):
        # 关闭常见站内弹窗/蒙层，避免遮挡点击
        selectors = [
            # 常见按钮
            (By.XPATH, "//button[normalize-space(text())='确定' or normalize-space(text())='知道了' or normalize-space(text())='我知道了' or normalize-space(text())='好的' or normalize-space(text())='OK' or normalize-space(text())='关闭']"),
            (By.XPATH, "//a[normalize-space(text())='确定' or normalize-space(text())='知道了' or normalize-space(text())='我知道了' or normalize-space(text())='好的' or normalize-space(text())='OK' or normalize-space(text())='关闭']"),
            # 常见弹窗库的确认按钮
            (By.CSS_SELECTOR, '.swal2-confirm, .el-message-box__btns .el-button--primary, .modal .btn-primary'),
            # 右上角关闭图标
            (By.CSS_SELECTOR, '.swal2-close, .el-message-box__close, .modal .close, .ant-modal-close')
        ]
        for _ in range(max_rounds):
            dismissed_in_round = False
            for by, sel in selectors:
                try:
                    elems = driver.find_elements(by, sel)
                    for e in elems:
                        if e.is_displayed():
                            try:
                                driver.execute_script('arguments[0].scrollIntoView({block: "center"});', e)
                                time.sleep(0.05)
                                try:
                                    e.click()
                                except Exception:
                                    driver.execute_script('arguments[0].click();', e)
                                time.sleep(0.2)
                                dismissed_in_round = True
                            except Exception:
                                continue
                except Exception:
                    continue
            if not dismissed_in_round:
                break

    def is_already_checked_in(short_wait: int = 3) -> bool:
        # 先判断“已签到”态：禁用样式按钮且文本包含“已签到”
        try:
            success_btn = WebDriverWait(driver, short_wait).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    'a.btn.btn-transparent-white.font-weight-bold.py-3.px-6.mr-2.disabled'
                ))
            )
            text = (success_btn.text or '').strip()
            cls = (success_btn.get_attribute('class') or '').lower()
            disabled_attr = success_btn.get_attribute('disabled')
            if '已签到' in text or disabled_attr is not None or 'disabled' in cls:
                return True
        except TimeoutException:
            pass

        # 再判断“未签到”态：#checkin 按钮存在且可显示、可点击
        try:
            btn = WebDriverWait(driver, short_wait).until(
                EC.presence_of_element_located((By.ID, 'checkin'))
            )
            text = (btn.text or '').strip()
            onclick_attr = (btn.get_attribute('onclick') or '')
            disabled_attr = btn.get_attribute('disabled')
            if disabled_attr is not None:
                return True
            if (('每日签到' in text) or ('checkin' in onclick_attr)) and btn.is_displayed():
                return False
        except TimeoutException:
            pass

        return False

    def find_login_button(max_wait: int = 10):
        locators = [
            (By.ID, 'login_submit'),
            (By.CSS_SELECTOR, '#login_submit'),
            (By.CSS_SELECTOR, 'button#login_submit'),
            (By.CSS_SELECTOR, 'a#login_submit'),
            (By.CSS_SELECTOR, 'button[type="submit"]'),
            (By.XPATH, "//button[contains(normalize-space(.), '登录') or contains(., 'Login')]"),
            (By.XPATH, "//a[contains(normalize-space(.), '登录') or contains(., 'Login')]")
        ]
        end_time = time.time() + max_wait
        last_err = None
        while time.time() < end_time:
            for by, sel in locators:
                try:
                    elem = driver.find_element(by, sel)
                    if elem and elem.is_displayed():
                        return elem
                except Exception as e:
                    last_err = e
            time.sleep(0.2)
        if last_err:
            raise last_err
        return None

    # 确保不在 iframe 中
    try:
        driver.switch_to.default_content()
    except Exception:
        pass

    # 登录表单交互
    email_input = WebDriverWait(driver, 60).until(
        EC.visibility_of_element_located((By.ID, "email"))
    )
    passwd_input = WebDriverWait(driver, 60).until(
        EC.visibility_of_element_located((By.ID, "password"))
    )
    # 登录按钮可能有多种定位方式，增强定位稳健性
    try:
        login_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "login_submit"))
        )
    except TimeoutException:
        login_btn = find_login_button(max_wait=10)

    try:
        email_input.clear()
    except Exception:
        pass
    email_input.send_keys(ACCOUNT)
    # 触发前端框架输入监听
    try:
        driver.execute_script(
            "arguments[0].dispatchEvent(new Event('input', {bubbles:true}));"
            "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));",
            email_input
        )
    except Exception:
        pass

    try:
        passwd_input.clear()
    except Exception:
        pass
    passwd_input.send_keys(PASSWORD)
    try:
        driver.execute_script(
            "arguments[0].dispatchEvent(new Event('input', {bubbles:true}));"
            "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));",
            passwd_input
        )
    except Exception:
        pass

    # 点击登录前尝试关闭站内弹窗
    try_dismiss_site_dialogs(max_rounds=2)

    # 更稳健的点击登录（多重回退）
    clicked = False
    if login_btn is not None:
        try:
            clicked = safe_click(login_btn, desc='登录按钮', retries=3, wait_clickable=15)
        except Exception:
            clicked = False
    if not clicked:
        # 回退1：在密码框回车提交
        try:
            passwd_input.send_keys(Keys.ENTER)
            clicked = True
        except Exception:
            pass
    if not clicked:
        # 回退2：直接提交父 form
        try:
            form = email_input.find_element(By.XPATH, './ancestor::form')
            driver.execute_script('arguments[0].submit();', form)
        except Exception:
            pass

    # 等待页面完成并出现签到入口或页面发生变化
    # 等待页面加载与跳出登录页（或出现签到入口）
    try:
        wait_document_ready(20)
    except TimeoutException:
        pass
    try:
        wait_until_any([
            EC.presence_of_element_located((By.ID, 'checkin')),
            lambda d: '/auth/login' not in (d.current_url or ''),
            lambda d: 'user' in (d.current_url or ''),
            lambda d: 'dashboard' in (d.current_url or ''),
        ], timeout=30)
    except TimeoutException:
        time.sleep(1.5)

    # 登录后再次尝试关闭站内弹窗/公告
    try_dismiss_site_dialogs(max_rounds=3)

    # 签到流程
    print('正在检查签到状态')
    if is_already_checked_in(short_wait=3):
        print('今日已签到')
    else:
        print('今日未签到')
        # 签到按钮出现并可点击
        sign_in_btn = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.ID, 'checkin'))
        )
        print('正在签到')
        # 签到前先确保无遮挡
        try_dismiss_site_dialogs(max_rounds=2)
        safe_click(sign_in_btn, desc='签到按钮', retries=3, wait_clickable=10)

        # 等待签到状态切换为已签到
        try:
            WebDriverWait(driver, 25).until(lambda d: is_already_checked_in(short_wait=2))
            print('签到成功')
        except TimeoutException:
            # 回退等待并再次判断
            time.sleep(2)
            if is_already_checked_in(short_wait=2):
                print('签到成功')
            else:
                print('签到可能未成功，请人工确认')


if __name__ == '__main__':
    muniu_sign()
    driver.close()
    driver.quit()

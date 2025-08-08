# 牧牛自动签到（Selenium）

一个使用 Selenium 自动登录并进行“每日签到”的小脚本。

## 环境要求
- Python >= 3.12
- Google Chrome 已安装
- Windows：无需手动配置 chromedriver（Selenium 会自动处理）
- Linux：需要在配置中指定 `CHROME_DRIVER_PATH`

## 快速开始
1) 克隆项目后复制配置模板：
```bash
cp config-example.py config.py
```

2) 编辑 `config.py`：
- `ACCOUNT` / `PASSWORD`: 你的账号与密码
- `PROXY_STR`: 代理地址，例如 `http://127.0.0.1:7890`；若无代理，可将 `muniu_sign_selenium.py` 中的代理参数行移除或留空
- `CHROME_DRIVER_PATH`（仅 Linux 必填）: chromedriver 的绝对路径

3) 安装依赖（使用 uv）：
```bash
uv pip install selenium>=4.34.2
```

4) 运行：
```bash
uv run muniu_sign_selenium.py
```

## 可选设置
- 无头模式：已默认开启。如需可视化浏览器，将 `muniu_sign_selenium.py` 中的 `chrome_options.add_argument('--headless')` 注释掉。
- 证书与提示：脚本已默认忽略证书错误并关闭密码管理器/通知，减少弹窗干扰。

## 常见问题
- 代理/握手失败（如 net_error -100）：检查 `PROXY_STR` 是否可用，或移除代理参数后再试。
- 登录/签到按钮被遮挡：脚本会尝试自动关闭常见弹窗；若仍失败，请提供弹窗的 HTML 片段以便完善选择器。

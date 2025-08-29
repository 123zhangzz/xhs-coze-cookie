import os
from playwright.sync_api import sync_playwright
import requests
import sys

def get_xiaohongshu_cookie():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            # 判断是否已有登录状态
            state_file = "xhs_state.json"
            if os.path.exists(state_file):
                context = browser.new_context(storage_state=state_file)
                print("✔ 已加载保存的登录状态，无需扫码")
            else:
                context = browser.new_context()
                print("⚠ 未检测到登录状态，请扫码登录")

            page = context.new_page()
            page.goto("https://www.xiaohongshu.com/")

            # 如果第一次运行需要扫码
            if not os.path.exists(state_file):
                input(">>> 登录完成后，按下回车继续... ")
                context.storage_state(path=state_file)
                print("✔ 登录状态已保存，下次可自动登录")

            cookies = context.cookies()
            browser.close()

            cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
            return cookie_str

    except Exception as e:
        print("🚨 获取 Cookie 失败:", str(e))
        return None

def send_cookie_to_coze(cookie):
    if not cookie:
        print("❌ 无有效 Cookie，跳过发送")
        return

    # 从环境变量读取 Bearer Token
    bearer_token = os.getenv("COZE_BEARER_TOKEN")
    if not bearer_token:
        print("❌ 未设置环境变量 COZE_BEARER_TOKEN")
        sys.exit(1)

    # 你的 Webhook 地址（记得替换 bot_platform 和 biz_id）
    webhook_url = "https://api.coze.cn/api/trigger/v1/webhook/biz_id/bot_platform/hook/1000000000546794242"

    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "cookie": cookie
    }

    try:
        response = requests.post(webhook_url, json=payload, headers=headers)
        print("✅ Webhook 返回状态:", response.status_code)
        print("📨 返回内容:", response.text)

        # 如果不是 code: 0，提示用户检查
        if response.status_code == 200:
            resp_json = response.json()
            if resp_json.get("code") != 0:
                print("⚠️ Coze 返回异常，请确认是否已发布到正确渠道")
        else:
            print("❌ Webhook 请求失败，请检查 URL 或 Token")

    except Exception as e:
        print("🚨 发送 Webhook 失败:", str(e))


if __name__ == "__main__":
    cookie = get_xiaohongshu_cookie()
    send_cookie_to_coze(cookie)

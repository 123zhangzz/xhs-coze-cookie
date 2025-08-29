import os
from playwright.sync_api import sync_playwright
import requests

def get_xiaohongshu_cookie():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            if os.path.exists("xhs_state.json"):
                context = browser.new_context(storage_state="xhs_state.json")
                print("✔ 已加载保存的登录状态，无需扫码")
            else:
                context = browser.new_context()
                print("⚠ 未检测到登录状态，请扫码登录")

            page = context.new_page()
            page.goto("https://www.xiaohongshu.com/")

            if not os.path.exists("xhs_state.json"):
                input(">>> 登录完成后，按下回车继续... ")
                context.storage_state(path="xhs_state.json")  # 保存登录状态
                print("✔ 登录状态已保存，下次可自动登录")

            cookies = context.cookies()
            cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
            browser.close()
            return cookie_str
    except Exception as e:
        print("获取cookie失败:", e)
        return None

def send_cookie_to_coze(cookie):
    if not cookie:
        print("无有效cookie，跳过发送")
        return
    webhook_url = "https://api.coze.cn/api/trigger/v1/webhook/biz_id/bot_platform/hook/1000000000546754818"
    payload = {
        "cookie": cookie
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('COZE_BEARER_TOKEN')}"
    }
    try:
        response = requests.post(webhook_url, json=payload, headers=headers)
        print("Webhook 返回状态:", response.status_code)
        print("返回内容:", response.text)
    except Exception as e:
        print("发送Webhook失败:", e)

if __name__ == "__main__":
    cookie = get_xiaohongshu_cookie()
    send_cookie_to_coze(cookie)


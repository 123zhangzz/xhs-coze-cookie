from playwright.sync_api import sync_playwright
import requests
import json

def get_xiaohongshu_cookie():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state="xhs_state.json")

        page = context.new_page()
        page.goto("https://www.xiaohongshu.com/")

        print("请扫码登录小红书，扫码后按回车...")
        input(">> ")

        cookies = context.cookies()
        cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])

        context.storage_state(path="xhs_state.json")
        browser.close()
        return cookie_str

def send_cookie_to_coze(cookie):
    webhook_url = "https://api.coze.com/webhook/your-webhook-url"  # 替换为你的 Coze Webhook 地址
    payload = {
        "cookie": cookie
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(webhook_url, json=payload, headers=headers)
    print("Webhook 返回状态:", response.status_code)

if __name__ == "__main__":
    cookie = get_xiaohongshu_cookie()
    send_cookie_to_coze(cookie)

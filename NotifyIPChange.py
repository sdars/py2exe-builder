#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import os
import datetime
import locale
import concurrent.futures
import re
import json
import sys
import io
from collections import Counter

# ---------- 编码修复 (防止 Windows 控制台中文乱码) ----------
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ---------- 语言检测 ----------
try:
    lang_code, _ = locale.getlocale()
    if not lang_code:
        locale.setlocale(locale.LC_ALL, '')
        lang_code, _ = locale.getlocale()
    if not lang_code:
        lang_code = ''
except Exception:
    lang_code = ''

LANG = 'zh' if 'zh' in str(lang_code).lower() else 'en'

# ---------- 配置区 ----------
PUSH_URL = "https://sctapi.ftqq.com/SCT71314TA-GDdP0hf5dPCIHOH4uUYy11p4.send"
IP_APIS = [
    ("https://whois.pconline.com.cn/ipJson.jsp?ip=&json=true", lambda r: r.get("ip")),
    ("https://cdid.c-ctrip.com/model-poc2/h", lambda r: r.strip()),
    ("https://vv.video.qq.com/checktime?otype=ojson", lambda r: r.get("ip")),
    ("https://api.uomg.com/api/visitor.info?skey=1", lambda r: r.get("ip")),
    ("https://g3.letv.com/r?format=1", lambda r: r.get("remote")),
    ("https://qifu-api.baidubce.com/ip/local/geo/v1/district", lambda r: r.get("ip")),
    ("https://r.inews.qq.com/api/ip2city", lambda r: r.get("ip")),
    ("https://myip.ipip.net/json", lambda r: r["data"].get("ip")),
    ("https://api.live.bilibili.com/xlive/web-room/v1/index/getIpInfo", lambda r: r["data"].get("addr")),
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECORD_FILE = os.path.join(BASE_DIR, "ip_record.txt")

# ---------- 获取 IP ----------
def fetch_ip(entry):
    url, extractor = entry
    try:
        headers = {'User-Agent': 'curl/7.88.1'}
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            text = resp.text.strip()
            try:
                data = json.loads(text)
            except Exception:
                data = text
            ip = extractor(data)
            if isinstance(ip, str) and re.match(r'^\d{1,3}(\.\d{1,3}){3}$', ip):
                return url, ip
            return url, f"{'无效格式' if LANG == 'zh' else 'Invalid format'}: {ip}"
        return url, f"{'状态码' if LANG == 'zh' else 'Status'}: {resp.status_code}"
    except Exception as e:
        return url, f"{'错误' if LANG == 'zh' else 'Error'}: {e}"

def get_all_ips():
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_ip, entry) for entry in IP_APIS]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    return results

def extract_majority_ip(results):
    valid_ips = [res for _, res in results if re.match(r'^\d{1,3}(\.\d{1,3}){3}$', res)]
    if not valid_ips:
        return "无法获取" if LANG == 'zh' else "Unavailable"
    most_common_ip, _ = Counter(valid_ips).most_common(1)[0]
    return most_common_ip

# ---------- 构造推送内容 ----------
def build_push_content(current_ip, results, now):
    lines = []
    for url, res in results:
        is_main = (res == current_ip)
        prefix = "✅" if is_main else "⚠️"
        short_url = url.split("//")[-1].split("/")[0]
        lines.append(f"- {prefix} [{short_url}]({url}) → `{res}`")

    detail_block = "\n".join(lines)
    title = "公网 IP 变更通知" if LANG == 'zh' else "Public IP Change Notice"
    content = (
        f"### 🛰️ {title}\n\n"
        f"{'📅 时间' if LANG == 'zh' else '📅 Time'}：{now}\n"
        f"{'🌐 主 IP' if LANG == 'zh' else '🌐 Main IP'}：**`{current_ip}`**\n\n"
        f"{'🔍 接口返回详情' if LANG == 'zh' else '🔍 All API Responses'}：\n\n{detail_block}"
    )
    return content

# ---------- 文件处理 ----------
def load_last_record():
    if not os.path.exists(RECORD_FILE):
        return None
    with open(RECORD_FILE, 'r', encoding='utf-8') as f:
        return f.read().strip()

def save_record(content):
    with open(RECORD_FILE, 'w', encoding='utf-8') as f:
        f.write(content.strip())

# ---------- 推送通知 ----------
def push_notification(title, content, short=None):
    data = {
        "title": title,
        "desp": content,
    }
    if short:
        data["short"] = short

    try:
        resp = requests.post(PUSH_URL, data=data, timeout=5)
        if resp.status_code == 200:
            json_data = resp.json()
            if json_data.get("code") == 0:
                push_id = json_data.get("data", {}).get("pushid", "未知")
                print(f"推送成功，推送ID: {push_id}" if LANG == 'zh' else f"Push successful. ID: {push_id}")
            else:
                print(f"推送失败（业务错误）：{json_data}" if LANG == 'zh' else f"Push failed (logic): {json_data}")
        else:
            print(f"推送失败，状态码：{resp.status_code}" if LANG == 'zh' else f"Push failed, status: {resp.status_code}")
    except Exception as e:
        print("推送异常：" if LANG == 'zh' else "Push error:", e)

# ---------- 主程序 ----------
def main():
    print("正在获取公网 IP..." if LANG == 'zh' else "Getting public IP address...")
    results = get_all_ips()
    current_ip = extract_majority_ip(results)

    print("\n[ 所有接口返回 ]" if LANG == 'zh' else "\n[ All API Responses ]")
    for url, result in results:
        print(f"{url.ljust(60)} => {result}")
    print()

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record_text = f"IP: {current_ip}"
    push_content = build_push_content(current_ip, results, now)
    title = "IP变更通知" if LANG == 'zh' else "IP Change Detected"

    last = load_last_record()
    if last != record_text:
        print("IP 发生变化或无记录，正在推送..." if LANG == 'zh' else "IP changed or no record. Sending notification...")
        save_record(record_text)
        short_summary = f"IP: {current_ip}"
        push_notification(title, push_content, short=short_summary)
    else:
        print("IP 无变化，无需推送。" if LANG == 'zh' else "No change in IP. No notification sent.")

    print("当前状态：" if LANG == 'zh' else "Current status:")
    print(record_text)

if __name__ == '__main__':
    main()

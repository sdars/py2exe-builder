#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import os
import ipaddress
import datetime

chcp 65001

# ---------------- 配置区 ----------------
PUSH_URL = "https://sctapi.ftqq.com/SCT71314TA-GDdP0hf5dPCIHOH4uUYy11p4.send"

IPV4_APIS = [
    "http://ipv4.ip.sb",
    "http://api.ipify.org",
    "http://ifconfig.me/ip",
    "http://ipinfo.io/ip",
    "http://ipecho.net/plain",
]

IPV6_APIS = [
    "http://ipv6.ip.sb",
    "http://api6.ipify.org",
    "http://ifconfig.co/ip",
    "http://ident.me",
    "http://ipinfo.io/ip",
]
# ---------------------------------------

# 获取当前脚本所在目录，记录保存在同目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECORD_FILE = os.path.join(BASE_DIR, "ip_record.txt")


def is_valid_ipv4(ip):
    try:
        return isinstance(ipaddress.ip_address(ip), ipaddress.IPv4Address)
    except:
        return False


def is_valid_ipv6(ip):
    try:
        return isinstance(ipaddress.ip_address(ip), ipaddress.IPv6Address)
    except:
        return False


def try_multiple_sources(urls, version):
    headers = {
        'User-Agent': 'curl/7.88.1'
    }
    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            ip = response.text.strip()
            if "<html>" in ip.lower() or not ip:
                continue
            if version == "IPv4" and not is_valid_ipv4(ip):
                continue
            if version == "IPv6" and not is_valid_ipv6(ip):
                continue
            return ip
        except:
            continue
    return f"{version} 不可用"


def load_last_record():
    if not os.path.exists(RECORD_FILE):
        return None
    with open(RECORD_FILE, 'r', encoding='utf-8') as f:
        return f.read().strip()


def save_record(content):
    with open(RECORD_FILE, 'w', encoding='utf-8') as f:
        f.write(content.strip())


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
                print(f"推送成功，推送ID: {push_id}")
            else:
                print(f"推送失败（业务错误）：{json_data}")
        else:
            print(f"推送失败，状态码：{resp.status_code}")
    except Exception as e:
        print("推送异常：", e)


def main():
    print("正在获取当前公网 IP 地址...")
    ipv4 = try_multiple_sources(IPV4_APIS, "IPv4")
    ipv6 = try_multiple_sources(IPV6_APIS, "IPv6")

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = f"### IP 地址变更通知\n\n**时间：** {now}\n\n**IPv4：** `{ipv4}`\n\n**IPv6：** `{ipv6}`"
    record_text = f"IPv4: {ipv4}\nIPv6: {ipv6}"

    last = load_last_record()
    if last != record_text:
        print("IP 发生变化或无记录，更新记录并推送通知。")
        save_record(record_text)
        short_summary = f"IPv4: {ipv4} | IPv6: {ipv6}"
        push_notification("IP变更通知", result, short=short_summary)
    else:
        print("IP 无变化，无需推送。")

    print("当前状态：")
    print(record_text)


if __name__ == '__main__':
    main()

#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件  :ecloud_img_report.py
@说明  :定时扫描虚机中的clink等是否正常运行，websocket上报给业管
@时间  :2020/10/26 14:49:14
@作者  :dutianxing
@版本  :1.0
'''

import os
import time
import ctypes
import json
import random
import websocket
import hashlib
import subprocess as sp
from ctypes import *
import _thread as thread
import datetime
from glob import glob

# ============ 内嵌 PowerShell 类 ============
class PowerShell:
    def __init__(self, coding):
        cmd = [self._where('PowerShell.exe'),
               "-NoLogo", "-NonInteractive",
               "-Command", "-"]
        startupinfo = sp.STARTUPINFO()
        startupinfo.dwFlags |= sp.STARTF_USESHOWWINDOW
        self.popen = sp.Popen(cmd, stdout=sp.PIPE, stdin=sp.PIPE, stderr=sp.STDOUT, startupinfo=startupinfo)
        self.coding = coding

    def __enter__(self):
        return self

    def __exit__(self, a, b, c):
        self.popen.kill()

    def run(self, cmd, timeout=60):
        b_cmd = cmd.encode(encoding=self.coding)
        try:
            b_outs, errs = self.popen.communicate(b_cmd, timeout=timeout)
        except sp.TimeoutExpired:
            self.popen.kill()
            b_outs, errs = self.popen.communicate()
            errs = "False"
        try:
            outs = b_outs.decode('gbk', 'ignore')
        except UnicodeDecodeError:
            outs = ""
            errs = "False"
        return outs, errs

    @staticmethod
    def _where(filename, dirs=None, env="PATH"):
        if dirs is None:
            dirs = []
        if not isinstance(dirs, list):
            dirs = [dirs]
        if glob(filename):
            return filename
        paths = [os.curdir] + os.environ[env].split(os.path.pathsep) + dirs
        try:
            return next(os.path.normpath(match)
                        for path in paths
                        for match in glob(os.path.join(path, filename))
                        if match)
        except (StopIteration, RuntimeError):
            raise IOError("File not found: %s" % filename)

# ============ 核心逻辑 ============
class ImgReport:
    def check_clink(self):
        with PowerShell('GBK') as ps:
            out1, errs = ps.run("get-process clink_agent -ErrorAction SilentlyContinue")
        if out1:
            with PowerShell('GBK') as ps:
                out2, errs = ps.run("get-process clink_service -ErrorAction SilentlyContinue")
            if out2:
                return True
        return False

    def check_cloudbase(self):
        with PowerShell('GBK') as ps:
            out1, errs = ps.run("get-service cloudbase-init -ErrorAction SilentlyContinue")
        if out1:
            with PowerShell('GBK') as ps:
                out2, errs = ps.run(r"Test-Path 'C:\Program Files\Cloudbase Solutions\Cloudbase-Init\Python\Scripts\cloudbase-init.exe'")
            if out2.strip() == "True":
                return True
        return False

    def check_cloudupdate(self):
        try:
            filetime = os.path.getmtime(r"C:\Program Files (x86)\ctyun\clink\Mirror\CloudUpdate\logs\all.log")
            y = datetime.datetime.strptime(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(filetime)), '%Y-%m-%d %H:%M:%S')
            diff = datetime.datetime.now() - y
            return diff.total_seconds() < 172800
        except OSError:
            return False

def get_websocket_num():
    with PowerShell('GBK') as ps:
        out, errs = ps.run('(Get-ItemProperty -Path "HKLM:\\SOFTWARE\\ecloudsoft\\Mirror\\ClinkAgent" -Name "VersionCode").VersionCode')
    return 9 if int(out.strip()) > 101310000 else 7

def open_web_socket():
    APP_ID = 1007
    current_time = int(time.time())
    WEBSOCKET_DESK_REPORT = 7
    sign = compute_sign(APP_ID, current_time, WEBSOCKET_DESK_REPORT)
    if sign:
        with PowerShell('GBK') as ps:
            out, errs = ps.run("(Get-ItemProperty 'Registry::HKEY_LOCAL_MACHINE\\SOFTWARE\\ecloudsoft\\Mirror\\ClinkAgent' -Name 'WebSocketPort').WebSocketPort")
            try:
                port = int(out.strip())
            except:
                port = 9002
        websocket_url = f"ws://127.0.0.1:{port}?appid={APP_ID}&sign={sign}&t={current_time}&type={WEBSOCKET_DESK_REPORT}"
        websocket.enableTrace(False)
        ws = websocket.WebSocketApp(websocket_url,
                                    on_open=on_open,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)
        ws.run_forever()

def on_message(ws, message):
    pass

def on_error(ws, error):
    pass

def on_close(ws):
    pass

def on_open(ws):
    def run(*args):
        message = Message(result, remark)
        report_data = ReportData(102, message)
        json_str = json.dumps(report_data, default=lambda o: o.__dict__, ensure_ascii=False)
        ws.send(json_str)
        ws.close()
    thread.start_new_thread(run, ())

class Message:
    def __init__(self, result, remark):
        self.result = result
        self.remark = remark
        self.localtime = int(time.time())
    def write(self):
        return f"{{ result:{self.result}, remark:{self.remark}, time:{self.localtime}}}"

class ReportData:
    def __init__(self, bussType, message):
        self.bussType = bussType
        self.message = message
    def write(self):
        return f"{{ bussType:{self.bussType}, message:{self.message.write()}}}"

def compute_sign(app_id, current_time, websocket_type):
    info = get_secret()
    if info and info.contents.data:
        secret = bytes.decode(info.contents.data)
        input_string = f"{app_id}{secret}{current_time}{websocket_type}"
        return hashlib.sha256(input_string.encode("utf8")).hexdigest()
    return None

class Info(Structure):
    _fields_ = [("data", c_char_p), ("len", c_int)]

def get_secret():
    try:
        folder = r'C:\Program Files\Cloudbase Solutions\Cloudbase-Init\exe'
        dll_path = folder + r'\communicate.dll'
        lib = ctypes.cdll.LoadLibrary(dll_path)
        lib.GetInfo.argtypes = [c_int]
        lib.GetInfo.restype = POINTER(Info)
        return lib.GetInfo(5)
    except:
        return None

def execute(has_signal):
    if not has_signal:
        next_minute = (datetime.datetime.now() + datetime.timedelta(minutes=1)).replace(second=0, microsecond=0)
        current_time = next_minute.strftime("%H:%M")
        with PowerShell('GBK') as ps:
            outs, errs = ps.run("$env:username")
        username = outs.strip()
        execmd = r"""'C:\Program Files\Cloudbase Solutions\Cloudbase-Init\exe\ecloud_img_conf.exe' {'signalId':1,'command':25} """
        # 创建 ONCE 任务
        cmd = f'schtasks.exe /create /RU {username} /tn check_report_img_daily /tr "{execmd}" /SC ONCE /ST {current_time} /F /RL HIGHEST'
        with PowerShell('GBK') as ps:
            ps.run(cmd)
        # 创建 DAILY 任务
        cmd = f'schtasks.exe /create /RU {username} /tn check_report_img_daily /tr "{execmd}" /SC DAILY /ST {current_time} /RI 5 /DU 9999:59 /F /RL HIGHEST'
        with PowerShell('GBK') as ps:
            ps.run(cmd)
        return True

    global result, remark
    ir = ImgReport()
    if ir.check_clink():
        if ir.check_cloudbase() and ir.check_cloudupdate():
            result, remark = 1, 'success'
        else:
            result, remark = 3, 'failure'
    else:
        result, remark = 2, 'failure'
    open_web_socket()

# ============ 启动入口 ============
if __name__ == '__main__':
    result = 0
    remark = ''
    execute(has_signal=False)
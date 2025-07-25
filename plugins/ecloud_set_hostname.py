#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件  :ecloud_set_hostname.py
@说明  :修改虚机计算机名
@时间  :2020/10/23 16:34:02
@作者  :dutianxing
@版本  :1.0
'''
import sys
sys.path.append(".")
from get_meta_data import GetMetaData
import logging,time,requests,json,hashlib,urllib,winreg
from callpowershell import PowerShell
import tkinter
from tkinter import messagebox


class SetHostname():
    def execute(self,is_signal):
        logging.info("--------------------------------------SHN Start------------------------------------------")
        # 对比元数据中computername与当前hostname对比
        meta_hostname = GetMetaData().get_record_dll('computerName')
        if GetMetaData().get_record_meta('adname'):
            logging.info("meta data has adname, process stopped.")
            return False
        if meta_hostname:
            logging.info("the meta hostname is "+meta_hostname)
        else:
            logging.info('Could not find "computer name" from meta info.')
            return False
        
        with PowerShell('GBK') as ps:
            outs, errs = ps.run("hostname")
            old_hostname = outs
        logging.info("the current hostname is "+old_hostname)

        if old_hostname.strip() == meta_hostname.strip():
            logging.info("The computername is same with meta setting. Don't need another operation.")
            return True
        else:
            self.set_hostname(meta_hostname)
            # 如果由信令触发，则显示弹窗警示用户重启
            if is_signal:
                logging.info("The changging computername is called by signal, show user to restart instance.")
                # hide main window
                root = tkinter.Tk()
                root.withdraw()
                # message box display
                # 判断当前系统语言环境
                key=r"SYSTEM\CurrentControlSet\Control\Nls\Language"
                value_name="Default"
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key) as reg_key: 
                    value, type = winreg.QueryValueEx(reg_key, value_name)
                if value=="0804":
                    message_tittle='提示'
                    message_info='计算机名已修改，重启后生效，是否立刻重启？'
                else:
                    message_tittle='Tip'
                    message_info='The computer name has been modified and it will take effect after restarting. Do you want to restart immediately?'
                if messagebox.askyesno(message_tittle,message_info):
                    with PowerShell('GBK') as ps:
                        outs, errs = ps.run("Restart-Computer -force  -ErrorAction SilentlyContinue -WarningAction SilentlyContinue -ErrorVariable err")
                        logging.info(outs)
                        logging.info(errs)
                return True
            else:
                logging.info("The changging computername is called by startup, dont show the windows")
                return True

    def set_hostname(self,meta_hostname):
        # 设置cloudbase执行点，防止cloudbase后续执行覆盖结果
        with PowerShell('GBK') as ps:
            out,err=ps.run("(Get-ChildItem 'HKLM:\\SOFTWARE\\Cloudbase Solutions\\Cloudbase-Init\\').Name.Replace('HKEY_LOCAL_MACHINE','HKLM:')")
            pluginpath=out.strip()+"\\Plugins"
        logging.info(pluginpath)
        ps1="Set-ItemProperty '"+pluginpath+"' -name SetHostNamePlugin -Value 1"
        with PowerShell('GBK') as ps:
            out,err=ps.run(ps1)
            logging.info(out)
        
        # 设置hostname
        ps2="(Get-WMIObject  Win32_ComputerSystem).Rename('"+meta_hostname+"')"
        with PowerShell('GBK') as ps:
            outs, errs = ps.run(ps2)
            logging.info(outs)
            logging.error(errs)
    
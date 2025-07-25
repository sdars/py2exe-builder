#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件  :ecloud_reset_nic.py
@说明  :资源池切换vpc后，虚机内重启网卡
@时间  :2021/05/10 17:14:29
@作者  :dutianxing
@版本  :1.29
'''
import logging,platform,time
from callpowershell import PowerShell

class ResetNic():
    def execute(self):
        logging.info("--------------------------------------reset nic Start------------------------------------------")
        os_version=platform.release()
        if os_version.strip() == "10":
            logging.info("The os is windows server 2016")
            with PowerShell('GBK') as ps:
                outs, errs = ps.run("Get-NetAdapter -Name '以太网*' | Restart-NetAdapter")
            logging.info("Operation is successfully.")
            return True
        else:
            logging.info("The os is windows server 2008 r2")
            with PowerShell('GBK') as ps:
                outs, errs = ps.run("ipconfig /release")
                logging.info(outs)
            time.sleep(10)
            with PowerShell('GBK') as ps:
                outs, errs = ps.run("ipconfig /renew")
                logging.info(outs)
            logging.info("Operation is successfully.")
            return True
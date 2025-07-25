#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件  :unrequired_check.py
@说明  :自定义镜像，非必须项检查
@时间  :2021/06/23 17:23:48
@作者  :dutianxing
@版本  :1.0
'''
from callpowershell import PowerShell
import logging


class UnrequiredCheck:
    def check_net(self):
        #检查网络是否通外网
        logging.info("[net]Checking the net connection.")
        with PowerShell('GBK') as ps:
            outs, errs = ps.run("Test-Connection -Count 1 www.baidu.com -Quiet")
        if outs.strip() == "True":
            logging.info("[net]Trying connecting to baidu succesfully")
            return "True"
        else:
            logging.info("[net]Trying connecting to baidu failed")
            reason="外网访问异常"
            return reason
        
    
    
    def check_key_service(self):
        with PowerShell('GBK') as ps:
            out1, errs = ps.run("(get-service cloudbase-init).StartType")
        if out1.strip() == 'Disabled':
            logging.info("[service]Service cloudbase-init is disabled. It should be Manual or Automatic.")
            reason="cloudbase-init服务被禁用。"
        else:
            with PowerShell('GBK') as ps:
                out1, errs = ps.run("(get-service wuauserv).StartType")
            if not out1.strip() == 'Disabled':
                logging.info("[service]Service windows update is not disabled. It should be Disabled when mirror making.")
                reason="Windows update服务未被禁用"
            else:
                '''
                with PowerShell('GBK') as ps:
                    out1, errs = ps.run("(get-service LanmanServer).StartType")
                if out1.strip() == 'Disabled':
                    logging.info("[service]Service Server is disabled. Maybe influcing share printer fictions. It should be Manual or Automatic.")
                    reason="Server服务被禁用，可能会影响共享打印机等功能。"
                else:
                    logging.info("[service]Key service is configured correctly.")'''
                return "True"
        return reason
    
    def check_kms(self):
        with PowerShell('GBK') as ps:
            outs, errs = ps.run("cscript //nologo c:/windows/system32/slmgr.vbs /dli")
        templines=outs.strip().splitlines()
        for line in templines:
            if not line.find('已授权') == -1:
                logging.info(line)
                logging.info("[kms]The instance's kms is already actived.")
                return "True"
        logging.info("[kms]The instance's kms is not actived.")
        reason="虚机kms未授权"
        return reason
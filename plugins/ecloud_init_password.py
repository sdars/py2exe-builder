#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件  :ecloud_set_password.py
@说明  :通过cloudbase插件设置windows密码，取消自动登录
@时间  :2020/11/18 14:59:04
@作者  :dutianxing
@版本  :1.0
'''
import sys
sys.path.append(".")
from get_meta_data import GetMetaData
import logging,json,urllib,time,requests
from callpowershell import PowerShell
import datetime

class InitPassword():
    def execute(self):
        logging.info("---------------------------------------INIT PASS Start-------------------------------------")
        with PowerShell('GBK') as ps:
            out,err=ps.run("$env:username")
            logging.info(out)
        # 获取注册表，元数据
        reg_code=self.get_reg_code()
        meta_code=GetMetaData().get_record_dll('init_vm_password')
        
        if meta_code:
            logging.info("meta code is "+meta_code)   
        else:
            logging.info('Could not find the reset password version code message from meta data.')
            return False
        
        # 判断并执行重置密码
        if meta_code.strip() != reg_code:
            return self.set_password(reg_code,meta_code)
        else:
            logging.info("Meta data not change.")
            self.reset_conf_file()
            return False

    def set_password(self,reg_code,meta_code):
        # 重置密码
        self.reset_conf_file()
        self.change_conf_file()   # 修改conf文件
        if reg_code != "0":
            # 删除注册表
            with PowerShell('GBK') as ps:
                outs, errs = ps.run('Remove-Item "hklm:\software\cloudbase solutions\cloudbase-init"  -Force -Recurse')
                logging.info(outs)
            with PowerShell('GBK') as ps:
                out,err=ps.run("Set-ItemProperty -Path 'HKLM:\SOFTWARE\ecloudsoft\Mirror\InitPasswd' -Name VersionCode -Value 0")
                logging.info(out)
            logging.info("restart cloudbase.")
            self.restart_cloudbase()
            with PowerShell('GBK') as ps:
                out,err=ps.run("Stop-Service -Name cloudbase-init -force")
                logging.info(out)
            logging.info("stop service cloudbase now.")
            return 
        else:
            # 检测cloudbase是否运行结束后修改注册表
            while True:
                with PowerShell('GBK') as ps:
                    out,err=ps.run("(Get-ItemProperty -Path 'HKLM:\SOFTWARE\Cloudbase Solutions\Cloudbase-Init\*\Plugins\').InitUserPasswordPlugin") 
                logging.info("Cloudbase-init InitUserPasswordPlugin status is "+out.strip())
                if out.strip() == "1":
                    with PowerShell('GBK') as ps:
                        out,err=ps.run("Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\ecloudsoft\\Mirror\\InitPasswd' -Name VersionCode -Value "+str(meta_code)) 
                        logging.info(out)
                    #关闭自动登录
                    logging.info("Closing auto logon")
                    with PowerShell('GBK') as ps:
                        outs,errs = ps.run('Set-ItemProperty "HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon" -name "AutoAdminLogon" -value "0" ')
                        logging.info(outs)
                    #锁屏
                    logging.info("Locking screen.")
                    with PowerShell('GBK') as ps:
                        outs,errs = ps.run('(Get-WmiObject -Class Win32_OperatingSystem -ComputerName .).InvokeMethod("Win32Shutdown",4)')
                        logging.info(outs)
                    return
                else:
                    # 如果cloudbase还在运行，则等待30秒后重新检测
                    logging.info("wait 10 second, try more time.")
                    time.sleep(10) 

    def get_reg_code(self):
        #获取注册表中的记录数
        with PowerShell('GBK') as ps:
            out,err=ps.run("(Get-ItemProperty -Path 'HKLM:\SOFTWARE\ecloudsoft\Mirror\InitPasswd').VersionCode")
        try:
            reg_code=out.strip()
            int(reg_code)
        except ValueError:
            with PowerShell('GBK') as ps:
                ps.run("New-Item -Path 'HKLM:\SOFTWARE\ecloudsoft\Mirror' -Name 'InitPasswd'")
            with PowerShell('GBK') as ps:
                out,err=ps.run("Set-ItemProperty -Path 'HKLM:\SOFTWARE\ecloudsoft\Mirror\InitPasswd' -Name VersionCode -Value -1")
                logging.info(out)
            reg_code="-1"
        logging.info("Password Code from reg is "+str(reg_code)) 
        return reg_code
    
    def change_conf_file(self):
        # 修改cloudbase-init.conf文件进行修改
        # "C:\\Program Files\\Cloudbase Solutions\\Cloudbase-Init\\conf\\cloudbase-init.conf"
        filepath='C:\\Program Files\\Cloudbase Solutions\\Cloudbase-Init\\conf\\cloudbase-init.conf'
        lines = open(filepath, 'r',encoding='utf8').readlines()
        newlines = []
        for line in lines:
            newlines.append(line)
            if "groups=Administrators" in line:
                if "inject_user_password=true\n" not in lines:
                    newlines.append("inject_user_password=true\n")
            if "cloudbaseinit.plugins.common.sethostname.SetHostNamePlugin" in line:
                if "    cloudbaseinit.plugins.common.inituserpassword.InitUserPasswordPlugin,\n" not in lines:
                    newlines.append("    cloudbaseinit.plugins.common.inituserpassword.InitUserPasswordPlugin,\n") 
                    logging.info("change the cloudbase-init.conf file") 
        open(filepath, 'w',encoding='utf8').writelines(newlines)
        logging.info("cloudbase conf file is changed.")
        
    def reset_conf_file(self):
        #删除cloudbase-init.conf文件中的相关配置
        filepath='C:\\Program Files\\Cloudbase Solutions\\Cloudbase-Init\\conf\\cloudbase-init.conf'
        with open(filepath,'r') as r:
            lines=r.readlines()
        with open(filepath,'w') as w:
            for l in lines:
                if 'assword' not in l:
                    w.write(l)
        logging.info("cloudbase conf file is reset.")
    
    def restart_cloudbase(self):
        current_time=(datetime.datetime.now()+datetime.timedelta(seconds=65)).strftime("%H:%M")
        logging.info("Restart at "+current_time)
        execmd=r"""sc start cloudbase-init """
        cmd='schtasks.exe /create /RU system /tn restart_cloudbase /tr "'+execmd+'" /SC ONCE /ST '+current_time+' /F /RL HIGHEST'
        logging.info(cmd)
        with PowerShell('GBK') as ps:
            out, errs = ps.run(cmd)
            logging.info(out)
    '''
    def lock_screen(self):
        current_time=(datetime.datetime.now()+datetime.timedelta(seconds=10)).strftime("%H:%M")
        logging.info("Locking screen at "+current_time)
        execmd=r"""rundll32.exe user32.dll,LockWorkStation"""
        cmd='schtasks.exe /create /RU administrator /tn lock_screen /tr "'+execmd+'" /SC ONCE /ST '+current_time+' /F /RL HIGHEST'
        logging.info(cmd)
        with PowerShell('GBK') as ps:
            out, errs = ps.run(cmd)
            logging.info(out)'''
            
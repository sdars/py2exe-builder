#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件  :ecloud_set_password.py
@说明  :通过cloudbase插件重置windows密码，并设置自动登录
@时间  :2020/11/18 14:59:04
@作者  :dutianxing
@版本  :1.0
'''
import sys
sys.path.append(".")
from get_meta_data import GetMetaData
import logging,json,urllib,time,requests
from callpowershell import PowerShell

class SetPassword():
    def execute(self):
        logging.info("---------------------------------------SP Start-------------------------------------")
        with PowerShell('GBK') as ps:
            out,err=ps.run("$env:username")
            logging.info(out)
        # 获取注册表，元数据
        reg_code=self.get_reg_code()
        meta_code=GetMetaData().get_record_dll('reset_vm_password')
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
        self.change_conf_file()   # 修改conf文件
        if reg_code != "0":
            # 删除注册表
            with PowerShell('GBK') as ps:
                outs, errs = ps.run('Remove-Item "hklm:\software\cloudbase solutions\cloudbase-init"  -Force -Recurse')
                logging.info(outs)
            with PowerShell('GBK') as ps:
                out,err=ps.run("Set-ItemProperty -Path 'HKLM:\SOFTWARE\ecloudsoft\Mirror\ResetPasswd' -Name VersionCode -Value 0")
                logging.info(out)
            logging.info("restart computer.")
            with PowerShell('GBK') as ps:
                out,err=ps.run("Restart-Computer -force -ErrorAction SilentlyContinue -WarningAction SilentlyContinue -ErrorVariable err")
                return  # 第一次重启
        else:
            # 检测cloudbase是否运行结束，结束后修改注册表重启虚机
            while True:
                with PowerShell('GBK') as ps:
                    out,err=ps.run("(Get-ItemProperty -Path 'HKLM:\SOFTWARE\Cloudbase Solutions\Cloudbase-Init\*\Plugins\').SetUserPasswordPlugin") 
                logging.info("Cloudbase-init SetUserPasswordPlugin status is "+out.strip())
                if out.strip() == "1":
                    with PowerShell('GBK') as ps:
                        out,err=ps.run("Set-ItemProperty -Path 'HKLM:\SOFTWARE\ecloudsoft\Mirror\ResetPasswd' -Name VersionCode -Value "+str(meta_code)) 
                        logging.info(out)
                    logging.info("Cloudbase-init status is stopped, computer will be restarted.")
                    with PowerShell('GBK') as ps:
                        out,err=ps.run("Restart-Computer -force -ErrorAction SilentlyContinue -WarningAction SilentlyContinue -ErrorVariable err")   #第二次重启
                    return
                else:
                    # 如果cloudbase还在运行，则等待30秒后重新检测
                    logging.info("wait 10 second, try more time.")
                    time.sleep(10) 

    def get_reg_code(self):
        #获取注册表中的记录数
        with PowerShell('GBK') as ps:
            out,err=ps.run("(Get-ItemProperty -Path 'HKLM:\SOFTWARE\ecloudsoft\Mirror\ResetPasswd').VersionCode")
        try:
            reg_code=out.strip()
            int(reg_code)
        except ValueError:
            with PowerShell('GBK') as ps:
                ps.run("New-Item -Path 'HKLM:\SOFTWARE\ecloudsoft\Mirror' -Name 'ResetPasswd'")
            with PowerShell('GBK') as ps:
                out,err=ps.run("Set-ItemProperty -Path 'HKLM:\SOFTWARE\ecloudsoft\Mirror\ResetPasswd' -Name VersionCode -Value -1")
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
                if "inject_user_password=false\n" not in lines:
                    newlines.append("inject_user_password=false\nuser_password_length=10\nnetbios_host_name_compatibility=false\n")
            if "cloudbaseinit.plugins.common.sethostname.SetHostNamePlugin" in line:
                if "    cloudbaseinit.plugins.common.setuserpassword.SetUserPasswordPlugin,\n" not in lines:
                    newlines.append("    cloudbaseinit.plugins.common.setuserpassword.SetUserPasswordPlugin,\n") 
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
                if 'assword' not in l and 'compatibility' not in l:
                    w.write(l)
        logging.info("cloudbase conf file is reset.")

# !/usr/bin/env python
# -*- encoding: utf-8 -*-
# coding: utf-8
'''
@文件  :ecloud_set_visualeffect.py
@说明  :设置虚机窗口特效只保留平滑字体
@时间  :2020/10/23 16:34:38
@作者  :dutianxing
@版本  :1.0
'''
import logging
import logging.config
from callpowershell import PowerShell
from logging.handlers import TimedRotatingFileHandler

LOG_FILE = "C:\\Users\\Public\\Documents\\mirror\\Set_visualEffect.log"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
fh = TimedRotatingFileHandler(LOG_FILE,when='D',interval=1,backupCount=3)
datefmt = '%Y-%m-%d %H:%M:%S'
format_str = '%(asctime)s %(levelname)s %(message)s '
formatter = logging.Formatter(format_str, datefmt)
fh.setFormatter(formatter)
logger.addHandler(fh)
console = logging.StreamHandler()
console.setLevel(logging.INFO) 
formatter = logging.Formatter('[%(levelname)-8s] %(message)s') #屏显实时查看，无需时间
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

class SetVisuEff():
    def execute(self):
        logging.info("--------------------------Set Visual Effects start-----------------------------------------")
        #pscmd="(New-Object System.Security.Principal.NTAccount((Get-WmiObject Win32_ComputerSystem).UserName)).Translate([System.Security.Principal.SecurityIdentifier]).Value"
        with PowerShell('GBK') as ps:
            outs, errs = ps.run("powershell -inputformat none  -ExecutionPolicy Bypass -File 'C:\Program Files (x86)\ctyun\clink\Mirror\ScriptConfig\VisualFXSetting.ps1'")
            logging.info(outs)
            userSid=outs
        
        regpath="C:\Program Files (x86)\ctyun\clink\Mirror\ScriptConfig\VisualFXSetting.reg"
        oldvalue="HKEY_CURRENT_USER"
        newvalue="HKEY_USERS\\"+userSid
        
        # 全文替换
        '''
        with  open ( regpath , "r" ,encoding = 'utf-8' ,errors='ignore') as f:
            lines  =  f.readlines() 
        
        with  open ( regpath , "w" ,encoding = 'utf-8') as f_w:
            for  line  in  lines:
                if  "HKEY_CURRENT_USER"  in  line:
                    line  =  line.replace( "HKEY_CURRENT_USER" , newvalue )
                f_w.write(line)
                '''
        
        with PowerShell('GBK') as ps:
            outs, errs = ps.run('regedit /s "C:\Program Files (x86)\ctyun\clink\Mirror\ScriptConfig\VisualFXSetting.reg"')
            logging.info(outs)

SetVisuEff().execute()
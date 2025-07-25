import sys
sys.path.append(".")
from get_meta_data import GetMetaData
from callpowershell import PowerShell
import logging,time,json,sys,urllib
from urllib import request
from urllib import parse
from urllib.request import urlopen
import requests

class ADCheck():
    def execute(self):
        logging.info("--------------------------start Check AD Message-------------------------------------")
        local_domain = ""
        while len(local_domain) == 0:
            with PowerShell('GBK') as ps:
                outs, errs = ps.run('(Get-WmiObject -Class Win32_ComputerSystem | Select-Object Domain).Domain')
                local_domain = outs.strip()
        logging.info("The local domain is :"+local_domain)

        # 判断虚机是否已加域
        try:
            meta_domain = GetMetaData.get_record_dll('ad_domain_name')
            logging.info("The metadata doamin info is :"+meta_domain)
            # 关闭进程
            with PowerShell('GBK') as ps:
                outs, errs = ps.run('stop-process -name "ecloud_ADMain"')
            if local_domain == 'WORKGROUP':
                # 虚机未加域
                logging.info("The computer is not joined the AD Domain")
                return True
            elif local_domain == meta_domain:
                # 虚机与元数据域信息一致,开始退域
                logging.info("Start remove computer from AD...........")
                with PowerShell('GBK') as ps:
                    outs, errs = ps.run("Start-Process 'C:\\Program Files\\Cloudbase Solutions\\Cloudbase-Init\\ad\\ecloud_ADMain.exe' del")
                    logging.info(outs)
                time.sleep(5)
                with PowerShell('GBK') as ps:
                    outs, errs = ps.run('(Get-WmiObject -Class Win32_ComputerSystem | Select-Object Domain).Domain')
                    local_domain = outs.strip()
                    if local_domain == meta_domain:
                        # 退域失败，重试
                        logging.error("Removing computer from AD failed.")
                        return False
                    elif local_domain == 'WORKGROUP':
                        # 退域成功
                        logging.info("Removing computer succeed")
                        return True
            else:
                # 虚机与元数据域信息不一致，无法退域
                logging.info("The compurter domain info is not different with meta AD domain, can't remove computer")
                return False
        except KeyError:
            logging.info('Could not find the AD message from meta data.')    
            return True
        
   
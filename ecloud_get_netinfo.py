#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件  :ecloud_net_setting.py
@说明  :检查当前的网络状态，路由配置等并输出到脚本
@时间  :2021/01/28 16:35:15
@作者  :dutianxing
@版本  :1.0
'''

import  logging,platform,os,time,winreg,portalocker,sys
from callpowershell import PowerShell
from logging.handlers import TimedRotatingFileHandler

key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
public_path=winreg.QueryValueEx(key, "Common Documents")[0]
LOG_FILE = public_path+"\\mirror\\net_setting.log"
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

class NetInfo():
    def execute(self):
        logging.info("-----------------------------当前网络状态---------------------------------------------")
        with PowerShell('GBK') as ps:
            outs, errs = ps.run("ipconfig /all")
            logger.info(outs)
        logging.info("-----------------------------当前路由配置---------------------------------------------")
        with PowerShell('GBK') as ps:
            outs, errs = ps.run("route print -4")
            logger.info(outs)
        logging.info("-----------------------------当前防火墙配置---------------------------------------------")
        with PowerShell('GBK') as ps:
            outs, errs = ps.run("NetSh Advfirewall show allprofiles")
            logging.info(outs)
        logging.info("-----------------------------检测是否正常联网---------------------------------------------")
        os_version=platform.release()
        ## 新疆的网络环境，臨時
        with PowerShell('GBK') as ps:
            outs, errs = ps.run("ping -n 10 104.170.9.38 ")
            logger.info(outs)
        with PowerShell('GBK') as ps:
            outs, errs = ps.run("telnet 104.170.9.38 18816")
            logger.info(outs)
        with PowerShell('GBK') as ps:
            outs, errs = ps.run("Test-Connection -Count 1 www.baidu.com -Quiet")
        if outs.strip() == "True":
            logging.info("Trying connection ok")
        else:
            logging.info("Trying connection to baidu failed")
            if os_version.strip() == "10":
                logger.info("The os is windows server 2016")
                with PowerShell('GBK') as ps:
                    outs, errs = ps.run("Get-DnsClientServerAddress -InterfaceAlias 以太网* -AddressFamily IPv4 | Select-Object -ExpandProperty ServerAddresses")
                    logger.info("dns: "+outs)
                dns_list=outs.strip().splitlines()
                with PowerShell('GBK') as ps:
                    outs, errs = ps.run("Test-Connection -Count 1 14.215.177.39 -Quiet")
                if outs.strip() == "True":
                    logger.info("ping baidu ip address succeed. DNS maybe have problems.")
                    for dns_num in dns_list:
                        temp="Test-Connection -Count 1 "+dns_num+" -Quiet"
                        logger.info("Now run the command: "+temp)
                        with PowerShell('GBK') as ps:
                            outs, errs = ps.run(temp)
                            logger.info(outs)
                        if outs.strip() == "True":
                            value=1
                            break
                        else:
                            value=0
                    if value == 1:
                        for dns_num in dns_list:
                            temp="Resolve-DnsName www.baidu.com -Server "+dns_num+" -QuickTimeout"
                            logger.info("Now run the command: "+temp)
                            with PowerShell('GBK') as ps:
                                outs, errs = ps.run(temp)
                                logger.info(outs)
                            if outs.strip().split()[0] == "Resolve-DnsName":
                                logger.info("DNS request timed out. Try more time.")
                                value=0
                                continue
                            else:
                                logger.info("DNS TESTING is succeed.")
                                value=1
                                break
                        if value == 0:
                            for dns_num in ["114.114.114.114","223.5.5.5"]:
                                temp="Resolve-DnsName www.baidu.com -Server "+dns_num+" -QuickTimeout"
                                logger.info("Now run the command: "+temp)
                                with PowerShell('GBK') as ps:
                                    outs, errs = ps.run(temp)
                                    logger.info(outs)
                                if outs.strip().split()[0] == "Resolve-DnsName":
                                    logger.info("DNS request timed out. Try more time.")
                                    continue
                                else:
                                    logger.info("Please change DNS server addresses in ecloud desktop.")
                                    break
                                logger.info("DNS TESTING is falied. Problems maybe with the external network")
                    else:
                        logger.info("Every DNS ping test is failed.Problems maybe with the external network")   
                else:
                    logger.info("Net may have the problem.")
                    for dns_num in dns_list:
                        temp="Test-Connection -Count 1 "+dns_num+" -Quiet"
                        logger.info("Now run the command: "+temp)
                        with PowerShell('GBK') as ps:
                            outs, errs = ps.run(temp)
                            logger.info(outs)
                        if outs.strip() == "True":
                            value=1
                            logger.info("DNS TESTING is succeeded.")
                            break
                        else:
                            value=0
                    if value == 0:
                        for dns_num in dns_list:
                            temp="New-Object System.Net.Sockets.TcpClient -ArgumentList "+dns_num+",53"
                            logger.info("Now run the command: "+temp)
                            with PowerShell('GBK') as ps:
                                outs, errs = ps.run(temp)
                                logger.info(outs)
                            if outs.strip().split()[0] == "New-Object":
                                logger.info("DNS TESTING port 53 is failed . Try more time.")
                                continue
                            else:
                                logger.info("DNS TESTING is succeeded.")
                                break
                    with PowerShell('GBK') as ps:
                        outs, errs = ps.run("ping (Get-WmiObject win32_networkadapterconfiguration -filter \"Description='Red Hat VirtIO Ethernet Adapter'\").DefaultIPGateway[-1]")
                        logger.info("ping 网关： "+outs)
                    with PowerShell('GBK') as ps:
                        outs, errs = ps.run("Get-NetAdapter | Select-Object -Property Name,InterfaceDescription,Status")
                        logger.info("adapter:"+outs)
            else:
                logger.info("The os is windows server 2008 r2")
                with PowerShell('GBK') as ps:
                    outs, errs = ps.run("Get-WmiObject Win32_NetworkAdapter -Filter \"Name='Red Hat VirtIO Ethernet Adapter #2'\" | Select-Object -Property NetConnectionID,Name,MACAddress,NetworkAddresses,Speed")
                    logger.info("adapter:"+outs)
                with PowerShell('GBK') as ps:
                    outs, errs = ps.run("Get-WmiObject win32_networkadapterconfiguration -filter \"Description='Red Hat VirtIO Ethernet Adapter #2'\" | Select-Object  -ExpandProperty DNSServerSearchOrder")
                    logger.info("dns:"+outs)
                dns_list=outs.strip().splitlines()
                with PowerShell('GBK') as ps:
                    outs, errs = ps.run("Test-Connection -Count 1 14.215.177.39 -Quiet")
                if outs.strip() == "True":
                    logger.info("ping baidu ip address succeed. DNS maybe have problems.")
                    for dns_num in dns_list:
                        temp="Test-Connection -Count 1 "+dns_num+" -Quiet"
                        logger.info("Now run the command: "+temp)
                        with PowerShell('GBK') as ps:
                            outs, errs = ps.run(temp)
                            logger.info(outs)
                        if outs.strip() == "True":
                            value=1
                            break
                        else:
                            value=0
                    if value == 1:
                        for dns_num in dns_list:
                            temp="nslookup www.baidu.com "+dns_num
                            logger.info("Now run the command: "+temp)
                            with PowerShell('GBK') as ps:
                                outs, errs = ps.run(temp)
                                logger.info(outs)
                            if outs.strip().splitlines()[0] == "*** 请求 UnKnown 超时":
                                logger.info("DNS request timed out. Try more time.")
                                value=0
                                continue
                            else:
                                logger.info("DNS TESTING is succeed.")
                                value=1
                                break
                        if value == 0:
                            for dns_num in ["114.114.114.114","223.5.5.5"]:
                                temp="nslookup www.baidu.com "+dns_num
                                logger.info("Now run the command: "+temp)
                                with PowerShell('GBK') as ps:
                                    outs, errs = ps.run(temp)
                                    logger.info(outs)
                                if outs.strip().splitlines()[0] == "*** 请求 UnKnown 超时":
                                    logger.info("DNS request timed out. Try more time.")
                                    continue
                                else:
                                    logger.info("Please change DNS server addresses in ecloud desktop.")
                                    break
                                logger.info("DNS TESTING is falied. Problems maybe with the external network")
                    else:
                        logger.info("Every DNS ping test is failed.Problems maybe with the external network")   
                else:
                    logger.info("Net may have the problem.")
                    for dns_num in dns_list:
                        temp="Test-Connection -Count 1 "+dns_num+" -Quiet"
                        logger.info("Now run the command: "+temp)
                        with PowerShell('GBK') as ps:
                            outs, errs = ps.run(temp)
                            logger.info(outs)
                        if outs.strip() == "True":
                            value=1
                            logger.info("DNS TESTING is succeeded.")
                            break
                        else:
                            value=0
                    if value == 0:
                        for dns_num in dns_list:
                            temp="New-Object System.Net.Sockets.TcpClient -ArgumentList "+dns_num+",53"
                            logger.info("Now run the command: "+temp)
                            with PowerShell('GBK') as ps:
                                outs, errs = ps.run(temp)
                                logger.info(outs)
                            if outs.strip().split()[0] == "New-Object":
                                logger.info("DNS TESTING port 53 is failed . Try more time.")
                                continue
                            else:
                                logger.info("DNS TESTING is succeeded.")
                                break
            with PowerShell('GBK') as ps:
                outs, errs = ps.run("tracert www.baidu.com")
                logger.info("traceroute baidu:"+outs)
            with PowerShell('GBK') as ps:
                outs, errs = ps.run("tracert 114.114.114.114")
                logger.info("traceroute 114:"+outs)
                
    def _get_lock(self):
        file_name = os.path.basename(__file__)
        # linux等平台依然使用标准的/var/run，其他nt等平台使用当前目录
        if os.name == "posix":
            lock_file_name = "/var/run/{}.pid".format(file_name)
        else:
            lock_file_name = "{}.pid".format(file_name)
        self.fd = open(lock_file_name, "w")
        try:
            portalocker.lock(self.fd, portalocker.LOCK_EX | portalocker.LOCK_NB)
            # 将当前进程号写入文件
            # 如果获取不到锁上一步就已经异常了，所以不用担心覆盖
            self.fd.writelines(str(os.getpid()))
            # 写入的数据太少，默认会先被放在缓冲区，我们强制同步写入到文件
            self.fd.flush()
        except:
            logging.info("{} have another instance running.".format(file_name))
            sys.exit(0)
 
    def __init__(self):
        self._get_lock()
    
    # 和fcntl有点区别，portalocker释放锁直接有unlock()方法
    # 还是一样，其实并不需要在最后自己主动释放锁
    def __del__(self):
        portalocker.unlock(self.fd)

    
if __name__ == '__main__':
    try:
        ni=NetInfo()
        ni.execute()
        
    except BaseException as e:
        logging.exception(e)


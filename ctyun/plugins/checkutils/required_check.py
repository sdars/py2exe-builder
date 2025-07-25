#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件  :required_check.py
@说明  :自定义镜像检查项
@时间  :2021/06/23 14:54:20
@作者  :dutianxing
@版本  :1.0
'''
import sys,psutil
sys.path.append(".")
from get_meta_data import GetMetaData
from callpowershell import PowerShell
import logging,datetime,json,time,os,winreg

class RequiredCheck:
    def check_agent(self):
        # 判断进程clink_agent 和 clink_service是否存在
        with PowerShell('GBK') as ps:
            out1, errs = ps.run("get-process clink_agent  -ErrorAction SilentlyContinue") 
        if out1:
            with PowerShell('GBK') as ps:
                out2, errs = ps.run("get-process clink_service  -ErrorAction SilentlyContinue")
            if out2:
                logging.info("[agent]clink agent status is running.")
                return "True"
            else:
                logging.info("[agent]clink service status is unusual")
                reason="Clink Service 进程未被检测到。"
        else:
            logging.info("[agent]clink agent status is unusual")
            reason="Clink Agent 进程未被检测到。"
        return reason
    
    def check_cloudbase(self):
        #判断cloudbase服务和进程文件是否存在
        with PowerShell('GBK') as ps:
            out1, errs = ps.run("get-service cloudbase-init  -ErrorAction SilentlyContinue")
        if out1:
            with PowerShell('GBK') as ps:
                out2, errs = ps.run("Test-Path 'C:\Program Files\Cloudbase Solutions\Cloudbase-Init\Python\Scripts\cloudbase-init.exe'")
            if out2.strip() == "True":
                logging.info("[cloudbase]cloudbase is running")
                with PowerShell('GBK') as ps:
                    out1, errs = ps.run("(get-service cloudbase-init).StartType")
                if out1.strip() == 'Disabled':
                    logging.info("[service]Service cloudbase-init is disabled. It should be Manual or Automatic.")
                    reason="cloudbase-init服务被禁用。"
                else:
                    return "True"
            else:
                logging.info("[cloudbase]cloudbase-init process file is unusual")
                reason="cloudbase-init 进程异常。"
        else:
            logging.info("[cloudbase]cloudbase-init service status is unusual")
            reason="cloudbase-init 服务异常。"
        return reason
    
    def check_cloudupdate(self):
        #判断补丁升级功能是否正常，通过判断all.log日志的日期和当前日期相差不超过48小时为准
        for n in range(3):
            with PowerShell('GBK') as ps:
                outs, errs = ps.run("Start-Service W32Time | w32tm /resync")
        try:
            filetime=os.path.getmtime("C:\\Program Files (x86)\\ctyun\\clink\\Mirror\\CloudUpdate\\logs\\all.log")
            #filetime=os.path.getmtime("C:\\Program Files\\ctyun\\clink\\Mirror\\CloudUpdate\\logs\\all.log")
            h=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(filetime))#再由中间格式转为字符串(str)
            y =datetime.datetime.strptime(h, '%Y-%m-%d %H:%M:%S')
            z = datetime.datetime.now()
            diff = z - y
            logging.info("[cloudupdate] log date time is "+str(y))
            logging.info("[cloudupdate] now date time is "+str(z))
            logging.info("[cloudupdate] the diff time between all.log and now is "+str(diff))
            if diff.days < 2:
                logging.info("[cloudupdate]cloudupdate is running.")
                return "True"
            else:
                logging.info("[cloudupdate]cloudupdate is unusual.")
                reason="Cloudupdate程序异常。"
        except OSError as oe:
            logging.info("[cloudupdate]cloudupdate's log is not exist.")
            logging.info(oe)
            reason="Cloudupdate日志文件不存在。"
        return reason

    def check_software(self):
        ignore_list_str=GetMetaData().get_record_dll("detect_ignore_softwares")
        if ignore_list_str:
            ignore_list=ignore_list_str.split(",")
        else:
            ignore_list=[]
        with open('C:\Program Files (x86)\ctyun\clink\Mirror\ScriptConfig\ecloud_software_check.json','r',encoding='UTF-8') as json_file:
            soft_json = json.load(json_file)
        software_list=soft_json["software"]
        process_res=""
        service_res=""
        for software_item in software_list:
            software_name=software_item["name"]
            if software_name in ignore_list:
                continue
            process_list=software_item["process"]
            for process in process_list:
                with PowerShell('GBK') as ps:
                    out1, errs = ps.run("Get-Process -Name "+process+" -ErrorAction SilentlyContinue")
                if out1:
                    logging.info("[software]"+software_name+" process "+process+" exist in instance.")
                    if process_res:
                        process_res += ","
                    process_res += software_name
                    break
                else:
                    logging.info("[software]"+software_name+"process not found in instance.")
            service_list=software_item["service"]
            for service in service_list:
                with PowerShell('GBK') as ps:
                    out1, errs = ps.run("Get-Service -Name "+service+" -ErrorAction SilentlyContinue")
                if out1:
                    logging.info("[software]"+software_name+" service "+service+" exist in instance.")
                    if service_res:
                        service_res += ","
                    service_res += software_name
                    break
                else:
                    logging.info("[software]"+software_name+"service not found in instance.")
        if not (process_res or service_res):
            return "True"
        else:
            reason="云电脑内安装的"
            if process_res:
                reason += process_res+"进程，"
            if service_res:
                reason += service_res+"服务，"
            reason += "资源占用高，容易影响云电脑的使用体验。"
            return reason

    def check_kms(self):
        for i in range(3):
            with PowerShell('GBK') as ps:
                outs, errs = ps.run("cscript //nologo c:/windows/system32/slmgr.vbs /dli")
            templines=outs.strip().splitlines()
            for line in templines:
                if not line.find('已授权') == -1:
                    logging.info(line)
                    logging.info("[kms]The instance's kms is already actived.")
                    return "True"
            time.sleep(10)
            logging.info("kms is not actived,waiting 10s and try again.")
        logging.info("[kms]The instance's kms is not actived.")
        reason="虚机kms未授权。"
        return reason
    
    def check_time_sync(self):
        with PowerShell('GBK') as ps:
            out1, errs = ps.run("(get-service W32Time).StartType")
        if out1.strip() == 'Disabled':
            logging.info("[time]Service w32time is disabled. It should be Manual or Automatic.")
            reason="w32time服务已禁用。"
        else:
            for n in range(5):
                with PowerShell('GBK') as ps:
                    outs, errs = ps.run("Start-Service W32Time | w32tm /resync")
                templines=outs.strip().splitlines()
                for line in templines:
                    if not line.find('成功地执行了命令') == -1:
                        logging.info("[time]Time sync is succeed.")
                        return "True"
            logging.info("[time]Time sync is failed. Maybe Internet has problems.")
            reason="尝试时间同步失败，网络可能出现问题。"
        return reason
    
    def check_driver(self):
        acmd=r"""Get-WmiObject -Class Win32_PnPSignedDriver | Where-Object {$_.Description -eq "realtek ac'97 audio"}"""
        with PowerShell('GBK') as ps:
            out1, errs = ps.run(acmd,150)
        if out1:
            logging.info("[driver]AC'97 Driver is installed.")
            with PowerShell('GBK') as ps:
                out2, errs = ps.run("Get-WmiObject -Class Win32_PnPSignedDriver | Where-Object {$_.Description -eq 'Clouddesk Virtual USB Host Controller'}",150)
            if out2:
                logging.info("[driver]Clouddesk Virtual Bus Driver is installed.")
                return "True"
            elif errs == "False":
                logging.info("[driver]Clouddesk Virtual Bus Driver is Time OUT。")
                reason="虚拟总线驱动查询超时。"
            else:
                logging.info("[driver]Clouddesk Virtual Bus Driver is NOT installed. Try to find Fanxiushu Virtual USB Host Controller Driver.")
                with PowerShell('GBK') as ps:
                    out3, errs = ps.run("Get-WmiObject -Class Win32_PnPSignedDriver | Where-Object {$_.Description -eq 'Fanxiushu Virtual USB Host Controller'}",150)
                if out3:
                    logging.info("[driver]Fanxiushu Virtual USB Driver is installed.")
                    return "True"
                elif errs == "False":
                    logging.info("[driver]Fanxiushu Virtual USB Driver is Time OUT.")
                    reason="虚拟总线驱动查询超时。"
                else:
                    logging.info("[driver]Fanxiushu Virtual USB Driver is NOT installed.")
                    reason="虚拟总线驱动未正确安装。"
        elif errs == "False":
            logging.info("[driver]AC'97 Driver is Time OUT。")
            reason="声卡驱动查询超时。"
        else:
            logging.info("[driver]AC'97 Driver is NOT installed. Try to find  Clouddesk Audio Driver")
            with PowerShell('GBK') as ps:
                out3, errs = ps.run("Get-WmiObject -Class Win32_PnPSignedDriver | Where-Object {$_.Description -eq 'Clouddesk Audio Driver'}",150)
            if out3:
                logging.info("[driver]Clouddesk Audio Driver is installed.")
                return "True"
            elif errs == "False":
                logging.info("[driver]Clouddesk Audio Driver is Time OUT.")
                reason="声卡驱动查询超时。"
            else:
                logging.info("[driver]Clouddesk Audio Driver is NOT installed.")
                reason="声卡驱动未被正确安装。"
        return reason
    
    def check_wsus(self):
        i=4
        while i>0:
            with PowerShell('GBK') as ps:
                out2, errs = ps.run("Get-Process -Name TiWorker -ErrorAction SilentlyContinue")
            if out2:
                logging.info("[wsus]Tiworker.exe are still running,")
                cpu_percent=self.get_cpu_percent("TiWorker.exe")
                if cpu_percent > 5:
                    logging.info("[wsus]Tiworker.exe is using more than 5% CPU. wait 10s and retry.")
                    reason="系统更新进程TiWorker.exe占用CPU过高。"
                    time.sleep(10)
                    i -= 1
                    continue
                else:
                    logging.info("[wsus]Tiworker.exe is using less than 5% CPU.")
                    return "True"
            else:        
                logging.info("[wsus]TiWorker have been stopped.")
                with PowerShell('GBK') as ps:
                    out1, errs = ps.run("(get-service wuauserv).Status")
                if out1.strip() == 'Stopped':
                    logging.info("[wsus] windows update service is disabled.")
                    return "True" 
                else:
                    with PowerShell('GBK') as ps:
                        out1, errs = ps.run("""(New-Object -ComObject "Microsoft.Update.Session").CreateUpdateSearcher().Search("IsInstalled=0 and Type='Software'").Updates.Count""",30)
                    logging.info(out1)
                    if out1.strip() == '0':
                        logging.info("[wsus]No more WinUpdate sessions is waiting.")
                        return "True"    
                    elif len(out1.strip().splitlines()) >1:
                        logging.info("[wsus] wsus server maybe disabled or something wrong.")
                        reason="系统更新查询错误，网络可能存在问题。"
                    elif errs == "False":
                        logging.info("[wsus] update is TIME OUT.")
                        reason="系统更新查询超时，网络可能存在问题。"
                    else:
                        logging.info("[wsus]There are at least "+out1.strip()+" Windows update sessions whitch is not installed.")
                        reason="虚机中至少还有"+out1.strip()+"个更新未被安装。"
                break
                    
        return reason
    
    def get_cpu_percent(self,process_name):
        # 查找进程名对应的进程ID
        attrs = ['pid', 'name']
        for p in psutil.process_iter():
            try:
                pinfo = p.as_dict(attrs, ad_value='')
            except psutil.NoSuchProcess:
                pass
            else:
                if pinfo['name'] == process_name:
                    pid = pinfo['pid']
                    break
        else:
            logging.info("Process '{}' not found.".format(process_name))
            return None
        
        # 获取进程对象
        process = psutil.Process(pid)

        try:
            # 获取 CPU 百分比
            cpu_percent = process.cpu_percent(interval=1)
            logging.info("CPU percent for process '{}': {}%".format(process_name,cpu_percent))
            return cpu_percent
        except psutil.NoSuchProcess:
            logging.info("Process with PID {} no longer exists.".format(pid))
            return None
        except Exception as e:
            logging.exception(e)
            return None

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
            reason="外网访问异常。"
            return reason
        
    
    def check_key_service(self):
        with PowerShell('GBK') as ps:
            out1, errs = ps.run("(get-service cloudbase-init).StartType")
        if out1.strip() == 'Disabled':
            logging.info("[service]Service cloudbase-init is disabled. It should be Manual or Automatic.")
            reason="cloudbase-init服务被禁用。"
        else:
            with PowerShell('GBK') as ps:
                out1, errs = ps.run("(get-service wuauserv).Status")
            if not out1.strip() == 'Stopped':
                logging.info("[service]Service windows update is not disabled. It should be Disabled when mirror making.")
                reason="Windows update服务未被禁用。"
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
    
    def check_uac(self):
        logging.info("UAC]Checking the UAC is disabled.")
        key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System' 
        value_name_1 = 'EnableLUA'
        value_name_2 = 'ConsentPromptBehaviorAdmin'
        value_name_3 = 'FilterAdministratorToken'
        
        try: 
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key) as reg_key: 
                value_1, type_1 = winreg.QueryValueEx(reg_key, value_name_1)
                value_2, type_2 = winreg.QueryValueEx(reg_key, value_name_2)
                value_3, type_3 = winreg.QueryValueEx(reg_key, value_name_3)
                
            with PowerShell('GBK') as ps:
                out, errs = ps.run('(Get-WmiObject -Class Win32_OperatingSystem).Caption -like "*Server*"')
            if out.strip() == "True":
                logging.info("OS info is SERVER System. Need not check '以管理员批准模式运行所有管理员'.")
                value_1=0

            if value_1 == 0 and value_2 == 0 and value_3 == 0: 
                logging.info("UAC is disabled.")
                return "True"
            else:
                logging.info("UAC is enabled.")
                reason=""
                if value_1 != 0: 
                    logging.info("组策略'用户帐户控制：以管理员批准模式运行所有管理员'未被禁用")
                    reason+="组策略'用户帐户控制：以管理员批准模式运行所有管理员'未被禁用。\n"
                if value_2 != 0 :  
                    logging.info("用户账户控制未设置为'从不通知'")
                    reason+="用户账户控制未设置为'从不通知'\n"
                if value_3 != 0 :  
                    logging.info("组策略'用户帐户控制：用于内置管理员帐户的管理员批准模式'未被禁用。")
                    reason+="组策略'用户帐户控制：用于内置管理员帐户的管理员批准模式'未被禁用。\n"
                return reason
        except FileNotFoundError: 
            print("The specified registry key does not exist.")
            
    def check_detect(self):
        logging.info("[detect]Checking the component version is available.")
        detectList_str=GetMetaData().get_record_dll('windows-detect')  
        #detectList_str="ClinkAgent=102050010;Cloudbase=102050010;CloudUpdate=102050010;Launch=102050010"
        #string to dict
        detectList={}
        if not detectList_str:
            logging.info("[detect]No detect list from meta data.")
            return "True"
        for item in detectList_str.split(";"):
            key,value=item.split("=")
            logging.info("[detect]"+key+" version is "+value)
            detectList[key]=value
        #get version from regedit
        sub_key_start= r"Software\ecloudsoft\Mirror"
        failed_list=[]
        for key in detectList.keys():
            try:
                sub_key=sub_key_start+"\\"+key
                logging.info(sub_key)
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,sub_key) as reg_key: 
                    versionCode, type = winreg.QueryValueEx(reg_key, 'VersionCode')
                logging.info("[detect]"+key+" regedit version is "+str(versionCode))
                logging.info("[detect]"+key+" command version is "+detectList[key])
                if int(versionCode) >= int(detectList[key]):
                    logging.info("[detect]"+key+" version is OK.")
                else:
                    logging.info("[detect]"+key+" version is NOT OK.")
                    failed_list.append(key)
            except FileNotFoundError: 
                logging.info("[detect]The specified registry"+key+" does not exist.")
                failed_list.append(key)
                continue
        if failed_list:
            reason="以下组件版本不符合要求："
            for item in failed_list:
                reason += item+","
            return reason
        else:
            return "True"
            
            
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import subprocess
from ad.pwddecrypto import aes_ecb_decrypt,get_sha1prng_key
from get_meta_data import GetMetaData
from callpowershell import PowerShell
import sys,os,json,urllib,time,string,random,base64,requests,hmac,hashlib,winreg
from glob import glob
from datetime import datetime

import logging
import logging.config
import wmi

from urllib import request
from urllib import parse

class ADOperation():
    def execute(self):
        logging.info("-------------------------add-ad-start program------------------------------------------")
        #meta = self.get_record('meta')
        meta_info=GetMetaData().get_record_meta()
        try:
            name = meta_info['adname']
        except KeyError:
            name = meta_info['name']
        if self.is_base64_code(name):
            name_byte=base64.b64decode(name)
            meta_info['name']=bytes.decode(name_byte)
        logging.info(meta_info['name'])
        
        extend_info=GetMetaData().get_record_map(['ad_ou','ad_active_dns','ad_secondary_dns','ad_domain_name','ad_addition_account','ad_addition_pwd','ad_add_to_admingroup'])
        if not extend_info or extend_info == None:
            logging.info("can not get meta data from http service,exist program !!")
            sys.exit(0)
        meta=dict(meta_info,**extend_info)
        logging.info(meta)
        meta_hostname = meta_info['name'][0:15]
        logging.info("The meta hostname is :"+meta_info['name']+"and New hostname is"+meta_hostname)
        local_domain = ""
        while len(local_domain) == 0:
            with PowerShell('GBK') as ps:
                outs, errs = ps.run('(Get-WmiObject -Class Win32_ComputerSystem | Select-Object Domain).Domain')
                local_domain = outs.strip()
            with PowerShell('GBK') as ps:
                outs, errs = ps.run('(Get-WmiObject -Class Win32_ComputerSystem | Select-Object Name).Name')
                local_hostname = outs.strip()
        logging.info("The local domain is :"+local_domain)
        logging.info("The local hostname is :"+local_hostname)
        
        

        try:
            meta_domain = meta['ad_domain_name']
            meta_username = meta['ad_addition_account']
            meta_password = meta['ad_addition_pwd']
            logging.info("The metadata doamin info is :"+meta_domain)
            
            meta_password = self.decryptPwd(meta_domain,meta_username,meta_password)  #解密密文

            # 判断用户名是否有@域名后缀，有的话去掉
            surfix="@"+meta_domain
            if meta_username.endswith(surfix):
                name_length=len(meta_username) - len(surfix)
                meta_username=meta_username[:name_length]

            if local_domain == "WORKGROUP":
                # 虚机属于工作组，开始加域
                logging.info("joining the new domain")
                try:
                    ad_active_dns=meta['ad_active_dns']
                    ad_secondary_dns=meta['ad_secondary_dns']
                    dnslist = "'"+ad_active_dns+"','"+ad_secondary_dns+"'"
                except KeyError:
                    ad_active_dns=meta['ad_active_dns']
                    dnslist = "'"+ad_active_dns+"'"

                if local_hostname.strip().upper() not in meta_hostname.upper():
                    logging.info("Local computername is '"+local_hostname+"' is not same as meta hostname '"+meta_hostname+"' ")
                    with PowerShell('GBK') as ps:
                        result= ps.run("(Get-WmiObject -Class Win32_ComputerSystem).rename('{}','{}','{}').ReturnValue".format(meta_hostname,meta_password,meta_username))
                        result_code = result[0].replace("\r\n","")
                        logging.info("Rename computer name done,result = {}".format(result_code))
                        if result_code == "0":
                            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon', 0, winreg.KEY_WRITE)
                            winreg.SetValueEx(key, 'DefaultDomainName', ".\\", winreg.REG_SZ, meta_hostname)
                            winreg.CloseKey(key)
                            with PowerShell('GBK') as ps:
                                logging.info("Computer will be restart. ")
                                outs, errs = ps.run('shutdown /r /f /t 0 /c "rename computername by cloudbase-init"')
                        sys.exit(0) 
                
                
                JoinDomainResult = {}
                JoinDomainResult['0']="success"
                JoinDomainResult['5']="Access is denied."
                JoinDomainResult['87']="The parameter is incorrect."
                JoinDomainResult['110']="The system cannot open the specified object."
                JoinDomainResult['1323']="Unable to update the password."
                JoinDomainResult['1326']="Logon failure: unknown username or bad password."
                JoinDomainResult['1355']="The specified domain either does not exist or could not be contacted."
                JoinDomainResult['2224']="The account already exists."
                JoinDomainResult['2691']="The machine is already joined to the domain."
                JoinDomainResult['2692']="The machine is not currently joined to a domain."
                logging.info("+--------------------------------------------------------------------------------------------------------+")
                for key in JoinDomainResult:
                    logging.info(" JoinDomainOrWorkgroup code {} : {}".format(key,JoinDomainResult.get(key)))
                logging.info("+--------------------------------------------------------------------------------------------------------+")
                n = 1
                while n >0:
                    try:
                        ad_ou=meta['ad_ou']
                    except KeyError:
                        ad_ou=""
                    self.set_dns(dnslist)
                    # result=self.join_ad(ad_ou=ad_ou,dnslist=dnslist,ad_domain_name=meta_domain,ad_new_hostname=meta_hostname,ad_addition_account=meta_username,ad_addition_pwd=meta_password)
                    with PowerShell('GBK') as ps:
                        logging.info("(Get-WmiObject -Class Win32_ComputerSystem).JoinDomainOrWorkgroup('{}','{}','{}','{}',3).ReturnValue".format(meta_domain,meta_password,meta_username,ad_ou))
                        result= ps.run("(Get-WmiObject -Class Win32_ComputerSystem).JoinDomainOrWorkgroup('{}','{}','{}','{}',3).ReturnValue".format(meta_domain,meta_password,meta_username,ad_ou))
                        result_code = result[0].replace("\r\n","")
                        logging.info("Join Domain operation is done,result:{}".format(result_code))

                    

                    with PowerShell('GBK') as ps:
                        outs, errs = ps.run('(Get-WmiObject -Class Win32_ComputerSystem | Select-Object Domain).Domain')
                    local_domain = outs.strip()
                    if local_domain == meta_domain:
                        logging.info("Add Domain operation is succesful.")

                        #读取注册表，判断是否需要关闭自动登陆
                        # 打开注册表键
                        try:
                            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\ecloudsoft\Mirror\Cloudbase', 0, winreg.KEY_READ)
                            # 获取指定的键值
                            value, type = winreg.QueryValueEx(key, 'NoAutoLogon')
                            
                        except WindowsError as e:
                            logging.info("cloudbase NoAutoLogon 配置不存在,保持系统默认，不做处理")
                        else:
                            if value == 1:
                                logging.info("cloudbase NoAutoLogon 参数为 {},禁用默认自动登陆配置".format(value))
                                #关闭登录默认用户名
                                logging.info("Disappeared the Admin from logon screen.")
                                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System', 0, winreg.KEY_WRITE)
                                winreg.SetValueEx(key, 'dontdisplaylastusername', 0, winreg.REG_DWORD, 1)
                                
                                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon', 0, winreg.KEY_WRITE)
                                winreg.SetValueEx(key, 'AutoAdminLogon', 0, winreg.REG_DWORD, 0)
                            else:
                                logging.info("cloudbase NoAutoLogon 参数为 {},保持系统默认，不做处理".format(value))
                        finally:
                            winreg.CloseKey(key)
                        
                        # 给域账户赋管理员权限
                        # 检查元数据 ad_add_to_admingroup  （值是0或者1）? 读不到就默认1
                        add_to_admingroup=0
                        try:
                            add_to_admingroup=meta['ad_add_to_admingroup']
                        except KeyError:
                            logging.info("Cannot fing ad_add_to_admingroup from metadata")
                            add_to_admingroup=1
                        if int(add_to_admingroup) == 1:      # 2024-12-31 by tuzhidan：管理台接口全部是字符串类型
                            with PowerShell('GBK') as ps:
                                out3,err3=ps.run('net localgroup administrators "domain users" /add')
                                logging.info(out3)
                                logging.info("Adding Domain User to local admin group is done.")
                            with PowerShell('GBK') as ps:
                                out3,err3=ps.run('net localgroup "Remote Desktop Users" "domain users" /add')
                                logging.info(out3)
                                logging.info("Adding Domain User to Remote Desktop Users group is done.")
                        # 给admin账户设置一个随机密码，防止登录
                        # setpasswd="net user administrator "+self.get_random_passwd()
                        #with PowerShell('GBK') as ps:
                        #    out,err=ps.run(setpasswd)
                        #    logging.info(out) 
                        #    logging.info("Set administrator password as random password.")
                        # 回调接口
                        url = meta['patch_host']+'/api/openApi/cdserv/vmcallback/updateAddDomainResult'
                        uuid = meta['uuid']
                        self.post_status(url,uuid,1,"")
                        logging.info('The Computer joined the ActiveDomain successful.')
                        with PowerShell('GBK') as ps:
                            outs2,errs2 = ps.run('shutdown /r /f /t 0 /c "add active domain success,ready to restart"')
                        break
                    elif local_domain == "WORKGROUP":
                        n=n+1
                        logging.info("add computer failed , try more times")
                        if n==10:# 十次后上报错误信息
                            logging.info('add computer failed for 10 times , post the failed information')
                            try:
                                # result_lines=result.split('\n')
                                # while result_lines:
                                #     line=result_lines.pop(0)
                                #     if "Add-Computer :" in line:
                                #         break
                                # error_message=line+result_lines[0]
                                error_message = JoinDomainResult.get(result_code)
                                logging.info(error_message)
                                url = meta['patch_host']+'/api/openApi/cdserv/vmcallback/updateAddDomainResult'
                                uuid = meta['uuid']
                                self.post_status(url,uuid,0,error_message)
                            except ValueError as e:
                                logging.error("Could not found the Error Info.")
                                logging.info(e)
                                self.post_status(url,uuid,0,result)
                        time.sleep(5)
            elif local_domain == meta_domain:
                # 回调接口
                url = meta['patch_host']+'/api/openApi/cdserv/vmcallback/updateAddDomainResult'
                logging.info("url is "+url)
                uuid = meta['uuid']
                self.post_status(url,uuid,1,"")
                logging.info('The Computer already joined the ActiveDomain.')
            else:
                # 虚机域名与元数据不同，停止程序
                logging.info('The Computer already joined the other ActiveDomain,please remove first.')
        except Exception as e:
            logging.exception(e)
            logging.info('Could not find the AD message from meta data.')
            sys.exit(0)


    unpad = lambda s: s[:-ord(s[len(s) - 1:])]

    def get_random_passwd(self):
        chars=string.ascii_letters+string.digits
        return ''.join(random.sample(chars, 15))#得出的结果中字符不会有重复的

    def set_dns(self,dns_servers):
        try:
            # logging.info(dns_servers)
            adapters = wmi.WMI().Win32_NetworkAdapterConfiguration(IPEnabled = True)
            for adapter in adapters:
                # logging.info(adapter)
                if adapter.Description.startswith('Red Hat VirtIO Ethernet'):
                    logging.info("set adapter domain dns {},driver is {},mac is {}".format(dns_servers,adapter.Description,adapter.MACAddress))
                    # dns = adapter.DNSServerSearchOrder
                    new_dns=tuple(dns_servers.split(","))
                    # logging.info(new_dns)
                    adapter.SetDNSServerSearchOrder(new_dns)
                    logging.info("set dns {} success".format(dns_servers))
            
        except Exception as e:
            logging.exception(e)
            logging.info("Error setting DNS servers: {}".format(e))
            sys.exit(-1)

    def decryptPwd(self,domain_name,domain_account,domain_pass):
        # 获取key 解析密钥是：5fT0np!je&4@+加域域名+账号名
        key = "5fT0np!je&4@"+domain_name+domain_account
        logging.info(key)
        # 解码
        try:
            ad_decrypto_pwd = aes_ecb_decrypt(get_sha1prng_key(key), domain_pass)
            # logging.info(ad_decrypto_pwd)
            return ad_decrypto_pwd
        except Exception as e:
            logging.info("The password decrypto failed")
            logging.exception(e)
            return ""
        
    def join_ad(self,ad_ou,dnslist,ad_new_hostname,ad_domain_name,ad_addition_account,ad_addition_pwd):   
        
        
        # 加域
        # logging.info("starting the powershell script...")
       
        # ps1cmd = ".\\addcomputer.ps1 -DNS "+dnslist+" -Domain '"+ad_domain_name+"' -UserName '"+ad_addition_account+"' -Password '"+ad_decrypto_pwd+"'"
        ps1cmd = "powershell -file '..\\ctyun\\ad\\PsDomainAction.ps1' '{}' '{}' '{}' '{}' 1".format(ad_ou,ad_domain_name,ad_addition_account,ad_addition_pwd)
        '''
        if ad_ou:
            if ad_new_hostname:
                logging.info("Client write the ad OU.")
                ps1cmd = ".\\addcomputer.ps1 -OUInfo '"+ad_ou+"' -DNS "+dnslist+" -Domain '"+ad_domain_name+"' -NewComputerName '"+ad_new_hostname+"' -UserName '"+ad_addition_account+"' -Password '"+ad_decrypto_pwd+"'"
            else:
                ps1cmd = ".\\addcomputer.ps1 -OUInfo '"+ad_ou+"' -DNS "+dnslist+" -Domain '"+ad_domain_name+"' -UserName '"+ad_addition_account+"' -Password '"+ad_decrypto_pwd+"'"
        else:
            if ad_new_hostname:
                logging.info("Client dosent write the ad OU.")
                ps1cmd = ".\\addcomputer.ps1 -DNS "+dnslist+" -Domain '"+ad_domain_name+"' -NewComputerName '"+ad_new_hostname+"' -UserName '"+ad_addition_account+"' -Password '"+ad_decrypto_pwd+"'"
            else:
                ps1cmd = ".\\addcomputer.ps1 -DNS "+dnslist+" -Domain '"+ad_domain_name+"' -UserName '"+ad_addition_account+"' -Password '"+ad_decrypto_pwd+"'"
                '''

        with PowerShell('GBK') as ps:
            outs, errs = ps.run(ps1cmd)
        logging.info(outs)
        logging.error(errs)
        return outs

    def _where(filename, dirs=None, env="PATH"):
        """Find file in current dir, in deep_lookup cache or in system path"""
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

    def post_status(self,url,uuid,result,msg):
        requestData = {
            "osUuid":uuid, 
            "result":result,
            "msg":msg
        }
        try:
            api_key = '4c690cab8673148a6c3b002b2ef2b8f9'
            api_secret = '401e00dde77a2384c42937666fc8c2a4'
            now = datetime.now()
            timestamp = int(datetime.timestamp(now))
            headers = {
                'Content-Type': 'application/json'
            }
            data=json.dumps(requestData)
            #签名
            chars=string.ascii_letters+string.digits
            nonStr=''.join(random.sample(chars, 8))
            reqJson= hashlib.md5(data.encode("utf-8")).hexdigest()
            urlPre = "apiKey=" + api_key + "&nonStr=" + nonStr + "&reqJson=" + reqJson + "&timestamp=" + str(timestamp)
            sign = hashlib.md5((urlPre + api_secret).encode("utf-8")).hexdigest()
            posturl=url+"?" + urlPre + "&sign=" + sign #+"&osUuid="+uuid+"&result="+str(result)+"&msg="+msg
            logging.info(posturl)

            response = requests.post(url=posturl,headers=headers,data=data,verify=False)
            #response = urlopen(request_message)
            logging.info("the response message is :")
            logging.info(response.content)
            if response.content:
                logging.info(response.json())
        except Exception as e:
            logging.exception('post operation is failed')

    def is_base64_code(self,s):
        '''Check s is Base64.b64encode'''
        if not isinstance(s ,str) or not s:
            raise ValueError

        _base64_code = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
                        'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
                        'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a',
                        'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
                        'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                        't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1',
                        '2', '3', '4','5', '6', '7', '8', '9', '+',
                        '/', '=' ]

        # Check base64 OR codeCheck % 4
        code_fail = [ i for i in s if i not in _base64_code]
        if code_fail or len(s) % 4 != 0:
            return False
        return True

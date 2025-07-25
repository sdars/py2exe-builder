#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import subprocess
from ad.pwddecrypto import aes_ecb_decrypt,get_sha1prng_key
from callpowershell import PowerShell
from get_meta_data import GetMetaData
import sys,os,json,urllib,time,logging,base64,string,random,hmac,hashlib,requests
from glob import glob
from datetime import datetime

from urllib import request
from urllib import parse
from urllib.request import urlopen

class RemoveAD():
    def execute(self):
        logging.info("------------------------- Remove AD------------------------------------------")
        meta_info=GetMetaData().get_record_meta()
        try:
            name = meta_info['adname']
        except KeyError:
            name = meta_info['name']
        if self.is_base64_code(name):
            name_byte=base64.b64decode(name)
            meta_info['name']=bytes.decode(name_byte)
        extend_info=GetMetaData().get_record_map(['ad_ou','ad_active_dns','ad_secondary_dns','ad_domain_name','ad_addition_account','ad_addition_pwd','ad_add_to_admingroup'])
        if not extend_info or extend_info == None:
            logging.info("can not get meta data from http service,exist program !!")
            sys.exit(0)
        # logging.info("中文测试")     #中文打印正常      
        meta=dict(meta_info,**extend_info)
        meta_hostname = meta['name']
        logging.info("The meta hostname is :"+meta_hostname)
        local_domain = ""
        while len(local_domain) == 0:
            with PowerShell('GBK') as ps:
                outs, errs = ps.run('(Get-WmiObject -Class Win32_ComputerSystem | Select-Object Domain).Domain')
                local_domain = outs.strip()
        logging.info("The local domain is :"+local_domain)

        # 判断虚机是否已加域
        try:
            meta_domain = meta['ad_domain_name']
            meta_username = meta['ad_addition_account']
            meta_password = meta['ad_addition_pwd']
            try:
                ad_ou=meta['ad_ou']
            except KeyError:
                ad_ou=""
            logging.info("The metadata doamin info is :"+meta_domain)
            if local_domain == 'WORKGROUP':
                # 虚机未加域
                logging.info("Couldn't remove computer, this computer haven't add to any AD.")
                # 回调接口
                url = meta['patch_host']+'/api/openApi/cdserv/vmcallback/exitAddDomainResult'
                uuid = meta['uuid']
                self.post_status(url,uuid,0)

            elif local_domain == meta_domain:
                # 虚机与元数据域信息一致,开始退域
                logging.info("Start remove computer from AD...")
                meta_password = self.decryptoPwd(meta_domain,meta_username,meta_password)    # 解密密文
                # logging.info(meta_password)
                local_hostname = meta_hostname[0:15]
                logging.info("+--------------------------------------------------------------------------------------------------------+")
                logging.info("\tUnjoinDomainOrWorkgroup code 0 : success")
                logging.info("\tUnjoinDomainOrWorkgroup code 5 : Access is denied.")
                logging.info("\tUnjoinDomainOrWorkgroup code 1-4294967295 : other error")
                logging.info("+--------------------------------------------------------------------------------------------------------+")
                n=5
                while n>0:
                    # ps1cmd = "netdom remove {} /domain:{} /userd:{} /passwordd:{}".format(local_hostname,meta_domain,meta_username,meta_password)
                    with PowerShell('GBK') as ps:
                        result = ps.run("(Get-WmiObject -Class Win32_ComputerSystem).UnjoinDomainOrWorkgroup('{}','{}\{}',0).ReturnValue".format(meta_password,meta_domain,meta_username))
                        result_code = result[0].replace("\r\n","")  
                        logging.info("Unjoin Domain operation is done,result = {}".format(result_code))
                    
                    if result_code == "0":
                        with PowerShell('GBK') as ps:
                            result = ps.run("(Get-WmiObject -Class Win32_ComputerSystem).JoinDomainOrWorkgroup('WORKGROUP','','','',6).ReturnValue")
                            result_code = result[0].replace("\r\n","")  
                            logging.info("Join WorkGroup operation is done,result = {}".format(result_code))
                        
                    # ps1cmd = "powershell -file '..\\ctyun\\ad\\PsDomainAction.ps1' '{}' '{}' '{}' '{}' 0".format(ad_ou,meta_domain,meta_username,meta_password)
                    # logging.info(ps1cmd)
                    # self.remove_ad(ad_domain_name=meta['ad_domain_name'],ad_addition_account=meta['ad_addition_account'],ad_addition_pwd=meta['ad_addition_pwd'])
                    '''ad_addition_account=GetMetaData().get_record_extend('ad_addition_account')
                    ad_addition_pwd=GetMetaData().get_record_extend('ad_addition_pwd')
                    self.remove_ad(ad_domain_name=meta_domain,ad_addition_account=ad_addition_account,ad_addition_pwd=ad_addition_pwd)'''
                    # time.sleep(3)
                    # with PowerShell('GBK') as ps:
                    #     outs, errs = ps.run(ps1cmd)
                    # logging.info(outs)
                    # logging.error(errs)
                    # 重置administrator密码为空
                    pass

                    with PowerShell('GBK') as ps:
                        outs, errs = ps.run('(Get-WmiObject -Class Win32_ComputerSystem | Select-Object Domain).Domain')
                        local_domain = outs.strip()
                    if local_domain == meta_domain:
                        # 退域失败，重试
                        logging.info('Removing computer failed, try more times')
                        time.sleep(5)
                    elif local_domain == 'WORKGROUP':
                        # 退域成功
                        n=0
                        logging.info("Removing computer succeed")
                        # 回调接口
                        url = meta['patch_host']+'/api/openApi/cdserv/vmcallback/exitAddDomainResult'
                        #url = GetMetaData().get_record_meta('patch_host')+'/api/cdserv/vmcallback/exitAddDomainResult'
                        uuid = meta['uuid']
                        self.post_status(url,uuid,1)
            else:
                # 虚机与元数据域信息不一致，无法退域
                logging.info("The compurter domain info is not different with meta AD domain, can't remove computer")
                url = meta['patch_host']+'/api/openApi/cdserv/vmcallback/exitAddDomainResult'
                #url = GetMetaData().get_record_meta('patch_host')+'/api/cdserv/vmcallback/exitAddDomainResult'
                uuid = meta['uuid']
                self.post_status(url,uuid,0)

        except KeyError:
            logging.info('Could not find the AD message from meta data.')    

    unpad = lambda s: s[:-ord(s[len(s) - 1:])]

    def decryptoPwd(self,domain_name,domain_user,domain_pass):
        key = "5fT0np!je&4@"+domain_name+domain_user
        # 解码
        try:
            ad_decrypto_pwd = aes_ecb_decrypt(get_sha1prng_key(key), domain_pass)
            return ad_decrypto_pwd
        except Exception as e:
            logging.info("The password decrypto failed")
            logging.exception(e)
            return ""

    def remove_ad(self,ad_domain_name,ad_addition_account,ad_addition_pwd):
        key = "5fT0np!je&4@"+ad_domain_name+ad_addition_account
        try:
            ad_decrypto_pwd = aes_ecb_decrypt(get_sha1prng_key(key), ad_addition_pwd)
        except Exception as e:
            logging.info("The password decrypto failed")
            logging.exception(e)
            return False
        #退域
        logging.info("starting the powershell script...")
        ps1cmd = "powershell -file 'C:\\Program Files\\Cloudbase Solutions\\Cloudbase-Init\\ad\\removecomputer.ps1' -Domain '"+ad_domain_name+"' -UserName '"+ad_addition_account+"' -Password '"+ad_decrypto_pwd+"'"        
        #ps1cmd = ["PowerShell.exe", "-File", r"C:\\Program Files\\Cloudbase Solutions\\Cloudbase-Init\\ad\\removecomputer.ps1",
                  #"-Domain",ad_domain_name,"-UserName",ad_addition_account,"-Password",ad_decrypto_pwd]
        
        #cmdword=" ".join(ps1cmd)
        #logging.info(cmdword)
        #p=subprocess.Popen(ps1cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE).stdout.read().decode('cp936').encode('utf-8')
        #logging.info(p)
        
        #logging.info(ps1cmd)
        with PowerShell('GBK') as ps:
            outs, errs = ps.run(ps1cmd)
        logging.info(outs)
        logging.error(errs)
        # 重置administrator密码为空
        pass

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

    def post_status(self,url,uuid,res):
        requestData = {
            "osUuid":uuid, 
            "result":res
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
            logging.exception('post operation is faled')
    
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
        
'''
if __name__ == '__main__':
    ado = RemoveAD()
    ado.execute()
'''
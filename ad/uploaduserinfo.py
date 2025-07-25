# -*- coding: utf-8 -*-
from callpowershell import PowerShell
import logging
import logging.config
from urllib import request
from urllib import parse
from urllib.request import urlopen
import sys,os,json,urllib,time,logging,base64,requests,string,random,hmac,hashlib
from get_meta_data import GetMetaData
from datetime import datetime

class Uploaduserinfo():
    def execute(self):
        logging.info("-----------------------upload-ad-start program------------------------------------------")
        #meta = {}
        #meta = self.get_record('meta')
        meta_info=GetMetaData().get_record_meta()
        try:
            name = meta_info['adname']
        except KeyError:
            name = meta_info['name']
        if self.is_base64_code(name):
            name_byte=base64.b64decode(name)
            meta_info['name']=bytes.decode(name_byte)
        
        extend_info=GetMetaData().get_record_map(['ad_domain_name'])
        if not extend_info or extend_info == None:
            logging.info("can not get meta data from http service,exist program !!")
            sys.exit(0)
            
        meta=dict(meta_info,**extend_info)
        with PowerShell('GBK') as ps:
            outs, errs = ps.run('(Get-WmiObject -Class Win32_ComputerSystem | Select-Object Domain).Domain')
            local_domain = outs.strip()
            logging.info("local_domain is : "+local_domain)
        with PowerShell('GBK') as ps:
            outs, errs= ps.run('(Get-WmiObject -Class Win32_ComputerSystem | Select-Object Name).Name')
            local_hostname = outs.strip()
            logging.info("local_hostname is : "+local_hostname)
        n = 5
        while n>0:
            try:
                if meta['ad_domain_name'] == local_domain:
                    #如果已加域
                    logging.info("The computer already joined the domain.")
                    with PowerShell('GBK') as ps:
                        outs, errs = ps.run('(Get-ChildItem C:\\Users | ? {$_.Name -ne "public" -and $_.Name -ne "Administrator"} |Select-Object Name).Name')
                        accounts = outs
                        # 之后要考虑多账户的情况
                    if(accounts):
                        # 如果存在administrator外的账户目录
                        # logging.info(accounts)
                        #调接口
                        url = meta['patch_host']+'/api/openApi/cdserv/vmcallback/relateDomainAcct'
                        #url = GetMetaData().get_record_meta('patch_host')+'/api/cdserv/vmcallback/relateDomainAcct'
                        uuid = meta['uuid']
                        self.post_status(url,uuid,accounts)
                        logging.info('The account information upload sucessful.')
                        # 加域成功，关闭登录默认用户名
                        with PowerShell('GBK') as ps:
                            outs, errs = ps.run('Set-ItemProperty "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" -name "dontdisplaylastusername" -value "00000000" ')    
                        n=0
                    else:
                        n = n-1
                        logging.info("Not exist domain account logon, wait more time.")
                elif local_domain == "WORKGROUP":
                    #如果未加域
                    n=n-1
                    logging.info("the computer not joined the domain, wait more time")
            except KeyError:
                logging.info('Could not find the AD message from meta data.')
                sys.exit(0)

    '''
    def get_record(self,info):
        try:
            resp = urllib.request.urlopen('http://169.254.169.254/openstack/latest/meta_data.json')
            meta_json = json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            logging.exception("Could not get metadata, net may have trouble.")
            sys.exit(0)
        try:
            meta_data = meta_json[info]
        except KeyError:
            logging.error('Could not find meta info.')
        return meta_data'''
    
    def post_status(self,url,uuid,acct):
        requestData = {
            "osUuid":uuid, 
            "domainUserAcct":acct
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


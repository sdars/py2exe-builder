# -*- coding: utf-8 -*-
from ad.pwddecrypto import aes_ecb_decrypt,get_sha1prng_key
from callpowershell import PowerShell
from get_meta_data import GetMetaData
import sys,os,json,urllib,time,logging

from urllib import request
from urllib import parse
from urllib.request import urlopen
'''
logging.basicConfig(level = logging.DEBUG,
    format = '%(asctime)s %(levelname)-8s %(message)s', 
    datefmt = '%a, %d %b %Y %H:%M:%S',
    filename = '.\\AD.log',
    filemode = 'w')
console = logging.StreamHandler()
console.setLevel(logging.INFO) 
formatter = logging.Formatter('[%(levelname)-8s] %(message)s') #屏显实时查看，无需时间
console.setFormatter(formatter)
logging.getLogger().addHandler(console)
'''

class Post():
    def execute(self):
        logging.info("--------------------------start program------------------------------------------")
        meta_info=GetMetaData().get_record_meta()
        meta_hostname = meta_info['name']
        logging.info("The meta hostname is :"+meta_hostname)
        local_domain = ""
        while len(local_domain) == 0:
            with PowerShell('GBK') as ps:
                outs, errs = ps.run('(Get-WmiObject -Class Win32_ComputerSystem | Select-Object Domain).Domain')
                local_domain = outs.strip()
            with PowerShell('GBK') as ps:    
                outs, errs= ps.run('(Get-WmiObject -Class Win32_ComputerSystem | Select-Object Name).Name')
                local_hostname = outs.strip()
            
        logging.info("The local hostname is : "+local_hostname)
        logging.info("The local domain is : "+local_domain)
        
        uuid = meta_info['uuid']
        # arg1 = sys.argv[1] 
        # logging.info("arg1={}".format(arg1));
        # if arg1:
        #     uuid = arg1 
        url = meta_info['patch_host']+'/api/cdserv/vmcallback/updateAddDomainResult'
        
        self.post_status(url,uuid,1)
        logging.info('The Computer joined the ActiveDomain sucessful.')

        url = meta_info['patch_host']+'/api/cdserv/vmcallback/exitAddDomainResult'
        self.post_status(url,uuid,0)
    unpad = lambda s: s[:-ord(s[len(s) - 1:])]

    def post_status(self,url,uuid,result):
        requestData = {
            "osUuid":uuid, 
            "result":result
        }
        logging.info(requestData)
        try:
            data = parse.urlencode(requestData).encode('utf-8')
            request_message = request.Request(url, data)
            response = urlopen(request_message)
            logging.info(response.read().decode())
        except Exception as e:
            logging.exception('post operation is faled')
   
    
    # def get_record(self,info):
    #     try:
    #         resp = urllib.request.urlopen('http://169.254.169.254/openstack/latest/meta_data.json')
    #         meta_json = json.loads(resp.read())
    #     except Exception as e:
    #         logging.exception("Could not get metadata, net may have trouble.")
    #         sys.exit(0)
    #     try:
    #         meta_data = meta_json[info]
    #     except KeyError:
    #         logging.error('Could not find meta info.')
    #     return meta_data

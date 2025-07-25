#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件  :result_post.py
@说明  :创建虚机后检测cloudbase后回调上报给业管，放开客户端连接权限
@时间  :2020/10/23 16:34:38
@作者  :dutianxing
@版本  :1.0
'''
import sys
sys.path.append(".")
from get_meta_data import GetMetaData
import json,urllib,time, hashlib,requests,base64
from callpowershell import PowerShell
import logging
import logging.config
from logging.handlers import TimedRotatingFileHandler

try:
    LOG_FILE = 'C:\\Program Files\\Cloudbase Solutions\\Cloudbase-Init\\log\\RP.log'
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
except BaseException as e:
    sys.exit(0)


class PostOperation():
    def execute(self):
        logging.info("--------------------------Result Post start-----------------------------------------")
        url = GetMetaData().get_record_meta('patch_host')+'/api/cdserv/cloudupdate/sendFinishInfo'
        logging.info(url)

        uuid = GetMetaData().get_record_meta('uuid')
        name = GetMetaData().get_record_meta('name')
        if self.is_base64_code(name):
            name_byte=base64.b64decode(name)
            name=bytes.decode(name_byte)
        ACCESS_KEY = "cloud_desktop_2@19@@#$!!PPKJ"
        checksum = self.sha256_single(uuid+name+ACCESS_KEY)
        logging.info("checkSum is "+checksum)

        self.post_status(url,uuid,name,checksum)
        logging.info('The Computer initialization complete.')

    unpad = lambda s: s[:-ord(s[len(s) - 1:])]

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


    def sha256_single(self,value):
        """
        sha256加密
        :param value: 加密字符串
        :return: 加密结果转换为16进制字符串，并小写
        """
        hsobj = hashlib.sha256()
        hsobj.update(value.encode("utf-8"))
        return hsobj.hexdigest().lower()

    def post_status(self,url,uuid,name,checksum):
        requestData = {
            "osUuid":uuid, 
            "desktopName":name,
            "checkSum":checksum
        }
        logging.info(requestData)
        n=0
        while n<5:
            try:
                headers = {'Content-Type': 'application/json'}
                # verify=False 为绕过https的ssl加密
                response = requests.post(url=url,headers=headers,verify=False,data = json.dumps(requestData))
                #response = urlopen(request_message)
                logging.info("the response message is :")
                logging.info(response.content)
                if response.content:
                    logging.info(response.json())
                n=5
            except Exception as e:
                logging.exception('post operation is failed')
                n=n+1
                time.sleep(30)


if __name__ == '__main__':
    try:
        PostOperation().execute()
    except BaseException  as e:
        logging.exception(e)

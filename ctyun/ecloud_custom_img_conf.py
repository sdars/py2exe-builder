#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件  :ecloud_custom_img_conf_temp.py
@说明  :临时生成的单独数据清理程序，不被elcou_img_conf调用
@时间  :2020/10/23 16:32:18
@作者  :dutianxing
@版本  :1.0
'''
import sys
sys.path.append(".")
from get_meta_data import GetMetaData
import logging,time,requests,json,hashlib,urllib,os,glob,queue,base64
from callpowershell import PowerShell
from utils import ADCheck,cleanfile,cleanreg,cleanexplorer
from shutil import rmtree
from logging.handlers import TimedRotatingFileHandler

try:
    LOG_FILE = "C:\\Program Files\\Cloudbase Solutions\\Cloudbase-Init\\log\\MCU.log"
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

class CustomImgConf():
    def execute(self):
        logging.info("================================MCU Start===============================================")
        try:
            signal_id=sys.argv[1]
        except IndexError:
            signal_id=13
        
        cleanreg.CleanReg().execute()
        # time.sleep(5)
        cleanexplorer.CleanExplorer().execute()
        # time.sleep(10)
        cleanfile.CleanFile().execute()
        #ADCheck.ADCheck().execute(meta['meta'])
        
        # 回调
        statuscode=3
        meta_info=GetMetaData().get_record_meta()
        url = meta_info['patch_host']+'/api/cdserv/signal/reportSignalStatus'
        logging.info(url)
        uuid = meta_info['uuid']
        name = meta_info['name']
        if self.is_base64_code(name):
            name_byte=base64.b64decode(name)
            name=bytes.decode(name_byte)
        ACCESS_KEY = "cloud_desktop_2@19@@#$!!PPKJ"
        #uuid+desktopName+signalId+statusCode+accessKey
        checksum = self.sha256_single(uuid+name+str(signal_id)+str(statuscode)+ACCESS_KEY)
        logging.info("checkSum is "+checksum)
        if self.post_status(url,uuid,name,signal_id,statuscode,checksum):
            logging.info("Computer cleaning complete.")
    
    def post_status(self,url,uuid,name,signalId,statusCode,checksum):
        requestData = {
            "osUuid":uuid, 
            "desktopName":name,
            "signalId":signalId,
            "statusCode":statusCode,
            "checkSum":checksum
        }
        logging.info(requestData)
        n=0
        while n<5:
            try:
                headers = {'Content-Type': 'application/json'}
                response = requests.post(url=url,headers=headers,data=json.dumps(requestData),verify=False)
                #response = urlopen(request_message)
                logging.info("the response message is :")
                logging.info(response.content)
                if response.content:
                    logging.info(response.json())
                return True
            except Exception as e:
                logging.exception('post operation is failed')
                n=n+1
                time.sleep(10)
        return False

    unpad = lambda s: s[:-ord(s[len(s) - 1:])]

    def sha256_single(self,value):
        """
        sha256加密
        :param value: 加密字符串
        :return: 加密结果转换为16进制字符串，并小写
        """
        hsobj = hashlib.sha256()
        hsobj.update(value.encode("utf-8"))
        return hsobj.hexdigest().lower()
    
    def deleteOldPyinstallerFolders(self,time_threshold = 0): # Default setting: Remove after 1 hour, time_threshold in seconds
        logging.info("---clear _MEI files---")
        try:
            base_path = sys._MEIPASS
        except Exception as e:
            logging.exception(e)
            return  # Not being ran as OneFile Folder -> Return

        temp_path = os.path.abspath(os.path.join(base_path, '..')) # Go to parent folder of MEIPASS
        logging.info(temp_path)
        # Search all MEIPASS folders...
        mei_folders = glob.glob(os.path.join(temp_path, '_MEI*'))
        mei_folders.extend(glob.glob(os.path.join("C:\\", '_MEI*')))
        for item in mei_folders:
            logging.info(item)
            if (time.time()-os.path.getctime(item)) > time_threshold:
                try:
                    rmtree(item)
                except PermissionError:
                    logging.error("Permission Error for file "+item)
                    continue
    
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


try:
    CustomImgConf().execute()
except BaseException as e:
    logging.exception(e)
except ImportError as e:
    logging.exception(e)  
finally:
    if(hasattr(sys,"_MEIPASS")):#兼容非pyinstaller打包情况执行
        CustomImgConf().deleteOldPyinstallerFolders()
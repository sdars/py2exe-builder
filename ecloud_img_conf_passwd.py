#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件  :ecloud_img_conf.py
@说明  :镜像内设置集合
@时间  :2020/10/23 16:29:22
@作者  :dutianxing
@版本  :1.0
@修改  ：20210309 添加信令触发拉起img report
'''
import logging,sys,time,requests,json,hashlib,os,glob,base64,portalocker
from enum import IntEnum
from shutil import rmtree
from plugins.ecloud_set_password import SetPassword
from plugins.ecloud_init_password import InitPassword
import packaging
import packaging.version
import packaging.specifiers
import packaging.requirements
from logging.handlers import TimedRotatingFileHandler
from get_meta_data import GetMetaData

try:
    LOG_FILE = "C:\\Program Files\\Cloudbase Solutions\\Cloudbase-Init\\log\\PAS.log"
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

class ImgConf():
    def execute(self):
        logging.info("================================EIC===================================================")
        pid=os.getpid()
        cmdword="wmic process where(processid="+str(pid)+") get commandline /format:list"
        try: 
            self.run_utils(self.SignalSource.SIGNAL_RESET_PASSWORD,None)
            # time.sleep(2)
            self.run_utils(self.SignalSource.SIGNAL_INIT_PASSWORD,None)
            
        finally:
            if(hasattr(sys,'_MEIPASS')):
                self.deleteOldPyinstallerFolders()


    class SignalSource(IntEnum):
        SIGNAL_RESET_PASSWORD = 1001
        SIGNAL_INIT_PASSWORD = 1002


    def callback_signal(self,signal_id):
        logging.info("---start callback signal---")
        statuscode=3
        #回调
        meta_info=GetMetaData().get_record_meta()
        url = meta_info['patch_host']+'/api/cdserv/signal/reportSignalStatus'
        logging.info(url)
        '''弃用
        uuid = self.get_record('uuid')
        name = self.get_record('name')'''
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
            logging.info("Computer setting has finished.")
        

    def run_utils(self,command_id,args):
        if command_id == self.SignalSource.SIGNAL_RESET_PASSWORD:
            logging.info("command is for resetting passwords.")
            result=SetPassword().execute()
        elif command_id == self.SignalSource.SIGNAL_INIT_PASSWORD:
            logging.info("command is for init passwords.")
            result=InitPassword().execute()
        else:
            logging.error("command id not find")
            result=False
        return result
        

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
        while n<6:
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
    
    def deleteOldPyinstallerFolders(self,time_threshold = 36000): # Default setting: Remove after 1 hour, time_threshold in seconds
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
        mei_folders.extend(glob.glob(os.path.join("C:\\Windows\\Temp", '_MEI*')))
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

    def _get_lock(self):
        file_name = os.path.basename(__file__)
        print(file_name)
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
 
try:
    ic=ImgConf()
    ic.execute()
except BaseException as e:
    logging.error(e)
except:
    logging.error("something wrong without ensure exceptions.")
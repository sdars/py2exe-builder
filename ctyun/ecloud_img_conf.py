#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件  :ecloud_img_conf.py
@说明  :镜像内设置集合
@时间  :2020/10/23 16:29:22
@作者  :dutianxing
@版本  :1.0
@修改  :20210309 添加信令触发拉起img report
'''
import logging,sys,time,requests,json,hashlib,os,subprocess,glob,base64
import portalocker
from enum import IntEnum
from shutil import rmtree
from plugins.ecloud_custom_img_clean import CustomImgClean
from plugins.ecloud_set_hostname import SetHostname
from plugins.ecloud_set_password import SetPassword
from plugins.ecloud_init_password import InitPassword
from plugins.ecloud_sfs_action import SFSAction
from plugins.ecloud_reset_nic import ResetNic
import ecloud_img_report
from plugins.ecloud_custom_img_check import ImgCheck
import packaging
import packaging.version
import packaging.specifiers
import packaging.requirements
from logging.handlers import TimedRotatingFileHandler
from get_meta_data import GetMetaData
 
try:
    LOG_FILE = "C:\\Program Files\\Cloudbase Solutions\\Cloudbase-Init\\log\\EIC.log"
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
            cmdword.encode('gb2312')
            p=subprocess.Popen(cmdword, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE).stdout.read().decode('cp936').encode('utf-8')
            logging.info(p)
            #temp=str(p,encoding="unicode_escape").replace('\n', '').replace('\r', '').split()[3]
            temp=str(p,encoding='utf-8').replace('\n', '').replace('\r', '')
            logger.info(temp)
            str_arg = temp.split( ).pop(-1)
            #logging.Logger(str_arg) #兼容参数长度，始终取最后一个参数
            args=json.loads(str_arg) #兼容参数长度，始终取最后一个参数
            logging.info(args) 
            command_id=args['command']
            signal_id=args['signalId']
            logging.info("command id is "+str(command_id))
            logging.info("signalId id is "+str(signal_id))

            # 按信令不同，调用不同功能
            if self.run_utils(command_id,args):
                self.callback_signal(signal_id)
        except Exception as e:
            # logger.exception(e)
            # 无参数时说明非信令调用情况，每次运行以下组件
            logging.error("args  parameter is wrong, try some utils need to auto startup.")
            self.run_utils(self.SignalSource.SIGNAL_SET_HOSTNAME,None)
            time.sleep(2)
            '''
            self.run_utils(self.SignalSource.SIGNAL_RESET_PASSWORD,None)
            time.sleep(2)
            '''
            self.run_utils(self.SignalSource.SIGNAL_SFS_ACTION,{"data":{"action":5,'sfs_urls':None}})
            time.sleep(2)
            self.run_utils(self.SignalSource.SIGNAL_IMG_REPORT,False)
        #except:
            #logging.error("Something wrong. ")
        finally:
            if(hasattr(sys,"_MEIPASS")):#兼容非pyinstaller打包情况执行
                self.deleteOldPyinstallerFolders()
            

    class SignalSource(IntEnum):
        SIGNAL_CUSTOM_CONF = 13
        SIGNAL_SET_HOSTNAME = 16
        SIGNAL_RESET_PASSWORD = 1001
        SIGNAL_SFS_ACTION = 22
        SIGNAL_IMG_REPORT = 25
        SIGNAL_FUCTIONS = 27

    class TypeSource(IntEnum):
        Type_RESET_NIC = 1
        Type_IMG_CHECK = 2

    def callback_signal(self,signal_id):
        logging.info("---start callback signal---")
        statuscode=3
        #回调
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
            logging.info("Computer setting has finished.")
        

    def run_utils(self,command_id,args):
        # 按信令不同，调用不同功能
        if command_id == self.SignalSource.SIGNAL_CUSTOM_CONF:
            logging.info("command is for configing custom image.")
            result=CustomImgClean().execute()
        elif command_id == self.SignalSource.SIGNAL_SET_HOSTNAME:
            logging.info("command is for setting hostname.")
            if args:
                result=SetHostname().execute(True)
            else:
                result=SetHostname().execute(False)
        elif command_id == self.SignalSource.SIGNAL_RESET_PASSWORD:
            logging.info("command is for resetting passwords.")
            result=SetPassword().execute()
        elif command_id == self.SignalSource.SIGNAL_IMG_REPORT:
            logging.info("Command is for reporting img status.")
            if args:
                ecloud_img_report.execute(True)
            else:
                ecloud_img_report.execute(False)
            result=True
        elif command_id == self.SignalSource.SIGNAL_SFS_ACTION:
            logging.info("command is for operate something for sfs system.")
            action_mod=args['data']
            urls=list(filter(None,str(action_mod['sfs_urls']).strip('[]').split(',')))
            result=SFSAction().execute(action_mod['action'],urls)
        elif command_id == self.SignalSource.SIGNAL_FUCTIONS:
            action_mod=args['data']
            try:
                type_id=action_mod['type']
                if type_id == self.TypeSource.Type_RESET_NIC:
                    logging.info("command type is for reset nic.")
                    result=ResetNic().execute()
                elif type_id == self.TypeSource.Type_IMG_CHECK:
                    signal_id=args['signalId']
                    logging.info("command type is for custom image check.")
                    ImgCheck().execute(signal_id)
                    result=True
                else:
                    logging.error("type id not find")
                    result=False
            except KeyError as e:
                logging.info("type id could not found.")
                result=False
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
                time.sleep(30)
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
            logging.info(file_name+" have another instance running.")
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
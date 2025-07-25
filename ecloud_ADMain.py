#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import sys,logging,os,subprocess
import ad.adoperation as adoperation
import ad.removecomputer as removecomputer
import ad.uploaduserinfo as uploaduserinfo
import ad.post as post
from logging.handlers import TimedRotatingFileHandler

try:
    LOG_FILE = "C:\\Program Files\\Cloudbase Solutions\\Cloudbase-Init\\log\\AD.log"
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
    
class ADMain():
    def execute(self):    
        logging.info("================================AD Operate===================================================")
        pid=os.getpid()
        cmdword="wmic process where(processid="+str(pid)+") get commandline /format:list"
        try: 
            cmdword.encode('gb2312')
            p=subprocess.Popen(cmdword, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE).stdout.read().decode('cp936').encode('utf-8')
            logging.info(p)
            # arg1=str(p,encoding='utf-8').replace('\n', '').replace('\r', '').split()[3]
            temp=str(p,encoding='utf-8').replace('\n', '').replace('\r', '')
            logger.info(temp);
            arg1 = temp.split( ).pop(-1)
            logging.Logger(arg1)
            if arg1 == "add":
                adoperation.ADOperation().execute()
                sys.exit(0)
            elif arg1 == "del":
                removecomputer.RemoveAD().execute()
                sys.exit(0)
            elif arg1 == "upload":
                uploaduserinfo.Uploaduserinfo().execute()
                sys.exit(0)
            elif arg1 == "post": # 未使用
                post.Post().execute()
                sys.exit(0)
            elif arg1 == "all":
                adoperation.ADOperation().execute()
                uploaduserinfo.Uploaduserinfo().execute()
            else:
                sys.exit(0)
        except IndexError:
            sys.exit(0)
            
'''
try:
    ADMain().execute()
except BaseException as e:
    logging.error(e)
except:
    logging.error("something wrong without ensure exceptions.")'''
ADMain().execute()

'''
arg1 = sys.argv[1] 

try:
    if arg1 == "add":
        adoperation.ADOperation().execute()
        sys.exit(0)
    elif arg1 == "del":
        removecomputer.RemoveAD().execute()
        sys.exit(0)
    elif arg1 == "upload":
        uploaduserinfo.Uploaduserinfo().execute()
        sys.exit(0)
    elif arg1 == "post":
        post.Post().execute()
        sys.exit(0)
    else:
        logging.info(arg1)
        sys.exit(0)
except Exception as e:
    logging.info(e)
    logging.info("processs stop with unexpected error.")
'''    

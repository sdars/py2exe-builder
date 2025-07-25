#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import platform,logging,random,os
from logging.handlers import TimedRotatingFileHandler

try:
    LOG_FILE = "C:\\Program Files\\Cloudbase Solutions\\Cloudbase-Init\\log\\task.log"
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

def set_defender_clean_task():
    win_version = platform.release()
    days = ["MON", "THU", "WED", "THU", "FRI", "SAT", "SUN"]
    day = random.randint(days.__len__())
    # logger.info(days[day])
    minute = random.randint(60)
    if minute < 10 :
        minute = "0" + str(minute)
    # logger.info(minute)
    # 禁用系统自带扫描计划

    logger.info("系统类型:" + platform.system() + " " + win_version)
    if win_version.__contains__("2008"):
        result = os.popen(r'schtasks /change /tn "\Microsoft\Windows Defender\MP Scheduled Scan" /disable')
        logger.info(result.read())
        result = os.popen(
            r'schtasks /delete /tn "\Microsoft\Windows Defender\ecloud Defender Scan Schedule" /f')
        logger.info(result.read())
        result = os.popen(r'schtasks /create /tn "\Microsoft\Windows Defender\ecloud Defender Scan Schedule" '
                        r'/tr "\"%ProgramFiles%\Windows Defender\MpCmdRun.exe\" Scan -ScheduleJob -WinTask '
                        r'-RestrictPrivilegesScan" /sc WEEKLY /mo 2 /d ' + days[day] + ' /st 02:' + str(minute) + ' /ru "System" /f')
        logger.info(result.read())
    else:
        result = os.popen(r'schtasks /change /tn "\Microsoft\Windows\Windows Defender\Windows Defender Scheduled '
                        r'Scan" /disable')
        logger.info(result.read())
        result = os.popen(
            r'schtasks /delete /tn "\Microsoft\Windows\Windows Defender\ecloud Defender Scan Schedule" /f')
        logger.info(result.read())
        result = os.popen(r'schtasks /create /tn "\Microsoft\Windows\Windows Defender\ecloud Defender Scan Schedule" '
                        r'/tr "\"%ProgramFiles%\Windows Defender\MpCmdRun.exe\" Scan -ScheduleJob" /sc WEEKLY /mo 2 '
                        r'/d ' + days[day] + ' /st 02:' + str(minute) + ' /ru "System" /f')
        logger.info(result.read())
    # 判断是否存在自定义计划


try:
    # 必须以管理员权限运行
    # 设置扫描时间随机
    if os.path.exists("%ProgramFiles%\Windows Defender\MpCmdRun.exe"):
        set_defender_clean_task()
    else:
        logger.info("Windows Defender Program not exist,exit ")
except BaseException as e:
    logging.error(e)
except:
    logging.error("something wrong without ensure exceptions.")

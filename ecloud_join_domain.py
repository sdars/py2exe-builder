#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import sys,logging
import ad.adoperation as adoperation
import ad.uploaduserinfo as uploaduserinfo
from get_meta_data import GetMetaData
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
    
    # console = logging.StreamHandler()
    # console.setLevel(logging.INFO) 
    # formatter = logging.Formatter('[%(levelname)-8s] %(message)s') #屏显实时查看，无需时间
    # console.setFormatter(formatter)
    # logging.getLogger().addHandler(console)
except BaseException as e:
    logging.exception(e)
    sys.exit(0)

extend_info=GetMetaData().get_record_map(['ad_domain_name'])

if not extend_info or extend_info == None:
    logger.info("+-----------------------------------------------------------------+")
    logger.info("can't get active domain meta data from http service,exist !!")
    logger.info("+-----------------------------------------------------------------+")
else:
    logger.info("+-----------------------------------------------------------------+")
    logger.info("\t begin to execute join domain Plugins")
    logger.info("+-----------------------------------------------------------------+")
    adoperation.ADOperation().execute()
    uploaduserinfo.Uploaduserinfo().execute() 
        
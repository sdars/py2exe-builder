#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件  :ecloud_custom_img_conf.py
@说明  :自定义镜像开始前激活，清理虚机内数据。
@时间  :2020/10/23 16:33:24
@作者  :dutianxing
@版本  :1.0
'''

import logging,sys,time,requests,json,hashlib,urllib

from utils import ADCheck,cleanfile,cleanreg,cleanexplorer

#C:\\Program Files\\Cloudbase Solutions\\Cloudbase-Init\\log

class CustomImgClean():
    def execute(self):
        logging.info("================================MCU Start===============================================")
        cleanreg.CleanReg().execute()
        time.sleep(5)
        cleanexplorer.CleanExplorer().execute()
        time.sleep(10)
        cleanfile.CleanFile().execute()
        #time.sleep(5)
        #ADCheck.ADCheck().execute()
        return True
        
        


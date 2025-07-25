#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件  :ecloud_custom_img_check.py
@说明  :自定义镜像制作检测和验收
@时间  :2021/06/22 17:00:46
@作者  :dutianxing
@版本  :1.30
'''

import sys
sys.path.append(".")
from get_meta_data import GetMetaData
import logging,time,websocket,hashlib,ctypes,json,random,urllib,requests,base64
from ctypes import *
import _thread as thread
from datetime import datetime
#import datetimeF
from plugins.checkutils.Check_item import CheckItem
from plugins.checkutils import required_check
from plugins.checkutils import unrequired_check
from callpowershell import PowerShell
from enum import Enum
from operator import methodcaller
from urllib import request
from urllib import parse
from urllib.request import urlopen



class ImgCheck():
    def execute(self,signalId):
        logging.info("--------------------------------------custom img check------------------------------------------")
        kms_must=GetMetaData().get_record_dll('kms_ignore')
        '''if kms_must == '1':
            logging.info("kms ignore ")
            check_list=[{"uac":1,"cloudbase":1,"cloudupdate":1},{"software":1,"kms":0},{"net":0,"key_service":0},{"driver":1,"wsus":1}]
            #check_list=[{"cloudbase":1,"cloudupdate":1},{"software":1,"kms":0},{"net":0,"key_service":0},{"driver":1,"wsus":1}]
        else:
            check_list=[{"uac":1,"cloudbase":1,"cloudupdate":1},{"software":1,"kms":1},{"net":0,"key_service":0},{"driver":1,"wsus":1}]
            #check_list=[{"cloudbase":1,"cloudupdate":1},{"software":1,"kms":1},{"net":0,"key_service":0},{"driver":1,"wsus":1}]'''
        if kms_must == '1':
            kms=0
        else:
            kms=1
        check_list=[{"uac":1,"detect":1},{"cloudbase":1,"cloudupdate":1},{"software":1,"kms":kms},{"net":0,"key_service":0},{"driver":1,"wsus":1}]
        #生成初始mirrorCheckResult
        mirrorCheckResult=[]
        for name in self.NameSource:
            key=name.name[5:]
            for timeout in self.TimeoutSource:
                if timeout.name == ("TIMEOUT_"+key):
                    break
            item={"name":name.value,"key":key.lower(),"timeout":timeout.value}
            mirrorCheckResult.append(item)
        message={"mirrorCheckResult":mirrorCheckResult,"mirrorCheckRemark":"success","mirrorCheckRemarkV26":"success"}
        # 分批检查并上报
        for n in range(len(check_list)):
            check_dict_now=check_list[n]
            message=self.get_message(message,check_dict_now)
            if n != len(check_list)-1:
                check_dict_next=check_list[n+1]
                for key,must in check_dict_next.items():
                    mirrorCheckResult=message["mirrorCheckResult"]
                    i=0
                    for result_item in mirrorCheckResult:
                        try:
                            if result_item["key"]==key:
                                if must == 1:
                                    mustCheck="True"    
                                else:
                                    mustCheck="False"
                                item={"name":result_item["name"],"key":key,"result":2,"mustCheck":mustCheck}
                                mirrorCheckResult.remove(result_item)
                                mirrorCheckResult.insert(i,item)
                        except KeyError:
                            pass
                        i+=1
                message["mirrorCheckResult"]=mirrorCheckResult
            message["signalId"]=signalId
            post_info=message.copy()
            if n != len(check_list)-1:
                post_info.pop("mirrorCheckRemark")
                
            self.post_message(post_info)
            time.sleep(10)
            
    def post_message(self,message):
        meta_info=GetMetaData().get_record_meta()
        message['osUuid']=meta_info['uuid']
        name = meta_info['name']
        if self.is_base64_code(name):
            name_byte=base64.b64decode(name)
            name=bytes.decode(name_byte)
        message['desktopName']=name
        message['osVersion']='Windows'
        logging.info(str(message))
        url = meta_info['patch_host']+'/api/cdserv/mirror/reportMirrorDetectRes'
        logging.info(url)
        self.post_status(url,message)

    def get_message(self,message:dict,check_item_list:dict):
        mirrorCheckResult=message["mirrorCheckResult"]
        checkRemark=0
        checkRemarkMax=0
        for key,must in check_item_list.items():
            checkRemarkMax += must
            if must == 1:
                mustCheck="True"    
            else:
                mustCheck="False"
            check_method=required_check.RequiredCheck()
            for msg in self.MsgSource:
                if msg.name == ("MSG_"+key.upper()):
                    break
            for name in self.NameSource:
                if name.name == ("NAME_"+key.upper()):
                    break
            for solution in self.SolutionSource:
                if solution.name == ("SOLUTION_"+key.upper()):
                    break
            for timeout in self.TimeoutSource:
                if timeout.name == ("TIMEOUT_"+key.upper()):
                    break
            func="check_"+key
            reason=methodcaller(func)(check_method)
            detectList=""
            if key == "detect":
                detectList=GetMetaData().get_record_dll('windows-detect')
            if reason == "True":
                chi_1=CheckItem(name.value,mustCheck,1,None,msg.value,solution.value,timeout.value,detectList)
                if must == 1:
                    checkRemark += 1
            else:
                if key == "detect":
                    checkRemark += 1
                    message["mirrorCheckRemarkV26"]="failure"
                chi_1=CheckItem(name.value,mustCheck,0,reason,msg.value,solution.value,timeout.value,detectList)
            logging.info(str(chi_1.get_value()))
            i=0
            for result_item in mirrorCheckResult:
                try:
                    if result_item["key"]==key:
                        mirrorCheckResult.remove(result_item)
                        mirrorCheckResult.insert(i,chi_1.get_value())
                except KeyError:
                    pass
                i+=1
        logging.info("checkRemark is "+str(checkRemark)+" and checkRemarkMax is "+str(checkRemarkMax))
        if message["mirrorCheckRemark"]=="success" and checkRemark==checkRemarkMax:
            message["mirrorCheckRemark"]="success"
        else:
            message["mirrorCheckRemark"]="failure"
        if message["mirrorCheckRemark"]=="success" and message["mirrorCheckRemarkV26"]=="success":
            message["mirrorCheckRemarkV26"]="success"
        else:
            message["mirrorCheckRemarkV26"]="failure"
        message["mirrorCheckResult"]=mirrorCheckResult
        return message
    
    
    def post_status(self,url,requestData):
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url=url,headers=headers,data=json.dumps(requestData),verify=False,timeout=5)
            #response = urlopen(request_message)
            logging.info("the response message is :")
            logging.info(response.content)
            if response.content:
                logging.info(response.json())
        except Exception as e:
            logging.exception('post operation is failed')
    
    class NameSource(Enum):
        # end with "check"
        NAME_CLOUDBASE="云电脑基础功能配置(Cloudbase)检查"
        NAME_CLOUDUPDATE="云电脑补丁升级检查"
        NAME_SOFTWARE="安全软件安装检查"
        NAME_KMS="Kms激活检查"
        NAME_NET="网络检查"
        NAME_KEY_SERVICE="系统服务检查"
        NAME_DRIVER="驱动检查"
        NAME_WSUS="系统补丁更新状态检查"
        NAME_UAC="系统UAC账户控制检查"
        Name_DETECT="系统组件版本检测检查"
        
    class MsgSource(Enum):
        MSG_CLOUDBASE="该项检查异常时，导致镜像初始化配置功能异常，严重影响云电脑功能使用，不可制作自定义镜像。"
        MSG_CLOUDUPDATE="该项检查异常时，导致对云电脑定期下发的补丁异常。严重影响云电脑功能使用，不可强行制作镜像。"
        MSG_SOFTWARE="该项检查异常时,此类软件资源占用高，容易影响云电脑的使用体验。"
        MSG_NET="该项检查异常时，可能会导致无法正常访问外网。"
        MSG_KMS="该项检查异常时，可能会导致新建虚机不能正常激活。"
        MSG_KEY_SERVICE="该项检查异常时，可能导致该镜像批量创建的云电脑同时进行系统升级，造成资源占用过高，影响云电脑的性能体验。"
        MSG_DRIVER="该项检查异常时,可能会导致声音播放异常,U盘识别异常等情况。"
        MSG_WSUS="该检查项异常时,桌面可能在进行windows系统补丁更新,影响桌面卡顿体验,不可制作自定义镜像。"
        MSG_UAC="该项检查异常时，可能会导致云电脑组件运行异常，严重影响云电脑功能使用，不可制作自定义镜像。"
        MSG_DETECT="该项检查异常时，可能会导致云电脑组件运行异常，严重影响云电脑功能使用，不可制作自定义镜像。"
        
    class SolutionSource(Enum):
        SOLUTION_CLOUDBASE="建议使用云电脑检测工具进行一键检测修复。若仍无法解决，请新开桌面制作自定义镜像。 "
        SOLUTION_CLOUDUPDATE="建议使用云电脑检测工具进行一键检测修复。若仍无法解决，请新开桌面制作自定义镜像。  "
        SOLUTION_SOFTWARE="请卸载软件并重启云电脑后，再重新制作自定义镜像。"
        SOLUTION_NET="建议使用云电脑检测工具进行一键检测修复。如用户无访问外网需求，可忽略。"
        SOLUTION_KMS="建议使用云电脑检测工具进行一键检测修复。若仍无法解决，请新开桌面制作自定义镜像。     "
        SOLUTION_KEY_SERVICE="建议禁用Windows update服务后,再重新制作自定义镜像。"
        SOLUTION_DRIVER="建议使用云电脑检测工具进行一键检测修复。若仍无法解决，请新开桌面制作自定义镜像。      "
        SOLUTION_WSUS="建议等待桌面更新完成后，再制作自定义镜像。"
        SOLUTION_UAC="建议关闭Windows UAC后,再重新制作自定义镜像。"
        SOLUTION_DETECT="建议下载最新版本组件补丁安装到虚机中，再制作自定义镜像。"
    
    class TimeoutSource(Enum):
        TIMEOUT_CLOUDBASE=60
        TIMEOUT_CLOUDUPDATE=60
        TIMEOUT_SOFTWARE=60
        TIMEOUT_NET=60
        TIMEOUT_KMS=60
        TIMEOUT_KEY_SERVICE=60
        TIMEOUT_DRIVER=300
        TIMEOUT_WSUS=120
        TIMEOUT_UAC=60
        TIMEOUT_DETECT=60
    
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

#ImgCheck().execute(123)

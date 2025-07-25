#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件  :Check_item.py
@说明  :自定义镜像检查项的实体类
@时间  :2021/06/29 15:41:17
@作者  :dutianxing
@版本  :1.0
'''

class CheckItem:
    def __init__(self, name, mustCheck=None,result=None,reason=None,msg=None,solution=None,timeout=None,detectList=None):
        self.__name = name
        self.__mustCheck = mustCheck
        self.__result = result
        self.__reason = reason
        self.__msg = msg
        self.__solution = solution
        self.__timeout = timeout
        self.__detectList = detectList
    
    def get_value(self):
        item={"name":self.__name,
              "mustCheck":self.__mustCheck,
              "result":self.__result,
              }
        if self.__reason:
            item["reason"]=self.__reason
        if self.__msg:
            item["msg"]=self.__msg
        if self.__solution:
            item["solution"]=self.__solution
        if self.__timeout:
            item["timeout"]=self.__timeout
        if self.__detectList:
            item["detectList"]=self.__detectList
        return item
        
    def set_name(self, name):
        self.__name = name
 
    def get_name(self):
        return self.__name

    def mustCheck(self, mustCheck):
        self.__mustCheck = mustCheck
 
    def get_mustCheck(self):
        return self.__mustCheck
    
    def set_result(self, result):
        self.__result = result
    
    def set_timeout(self, timeout):
        self.__timeout = timeout
 
    def get_result(self):
        return self.__result
    
    def set_reason(self, reason):
        self.__reason = reason
 
    def get_reason(self):
        return self.__reason

    def set_msg(self, msg):
        self.__msg = msg
 
    def get_msg(self):
        return self.__msg
    
    def set_solution(self, solution):
        self.__solution = solution
 
    def get_solution(self):
        return self.__solution
    
    def get_timeout(self):
        return self.__timeout
    
    def set_detectList(self, detectList):
        self.__detectList = detectList
    
    def get_detectList(self):
        return self.__detectList
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件  :get_meta_data.py
@说明  :获取元数据的新方案
@时间  :2021/10/18 15:27:37
@作者  :dutianxing
@版本  :1.0
'''

from callpowershell import PowerShell
import logging,json,requests,urllib,time,sys,string,random,hashlib
import ctypes
meta_data=None
class GetMetaData():

    def get_record_old(self,info):
        #弃用
        n=3
        while n>0:
            try:
                resp = urllib.request.urlopen('http://169.254.169.254/openstack/latest/meta_data.json',timeout=5)
                meta_json = json.loads(resp.read().decode('utf-8'))
            except Exception as e:
                logging.exception("Could not get metadata from http, net may have trouble.Waiting 10s and retry.")
                logging.error(e)
                time.sleep(10)
                n=n-1
                if n == 0:
                    return None
                continue
            logging.info(meta_json)
            logging.info(info)
            try:
                meta_data = meta_json[info]
                return meta_data
            except KeyError:
                logging.error('Could not find meta info from http, try to find in "meta".')
            try:
                meta_data = meta_json['meta'][info]
                return meta_data
            except KeyError:
                logging.error('Could not find meta info from http') 
            return None
    def get_record_old_map(self):
        #弃用
        n=3
        while n>0:
            try:
                resp = urllib.request.urlopen('http://169.254.169.254/openstack/latest/meta_data.json',timeout=5)
                meta_json = json.loads(resp.read().decode('utf-8'))
            except Exception as e:
                logging.exception("Could not get metadata from http, net may have trouble.Waiting 10s and retry.")
                logging.error(e)
                time.sleep(10)
                n=n-1
                if n == 0:
                    return None
                continue
            logging.info(meta_json)
            return meta_json['meta']
    
    def get_record_meta(self,info=None):
        global meta_data
        if meta_data:
            if info:
                if hasattr(meta_data,info):
                    return meta_data[info]
            else:
                return meta_data
        n=3
        while n>0:
            with PowerShell('GBK') as ps:
                outs, errs = ps.run("wmic computersystem get oemstringarray |findstr /v OEMStringArray")
                logging.info(outs.strip())
                if info:
                    logging.info("get meta data key [{}]".format(info))
            result_str=outs.strip()
            if result_str:
                try:
                    result_json = json.loads(result_str)
                    meta_data = result_json
                    if info:
                        return result_json[info]
                    else:
                        return result_json
                except KeyError:
                    logging.info('Could not find meta info  "'+info+'" from wmic.')
                    break
            else:
                logging.info("Could not get metadata from wmic, net may have trouble.Waiting 5s and retry.")
                time.sleep(5)
                n=n-1
                continue
        meta_data=None
        return meta_data
        
    
    def get_record_extend(self,info,is_retry=True):
        try:
            meta_info=self.get_record_meta()
            url = meta_info['patch_host']+'/api/openApi/cdserv/api/metadata/realTime/getMap'
            uuid = meta_info['uuid']
            api_key = '9f8b602b9d90314a24af41c11b459561'
            api_secret = '033d69ff3a6d6a2b2d14e5f7237e4166'
            nonStr = ''.join(random.sample(string.digits + string.ascii_letters,8))
            #logging.info(nonStr)
            current_time = int(time.time())
            url_pre = 'apiKey=' + api_key + '&codes=' + info + '&nonStr=' + nonStr + '&osUUID=' + uuid + '&timestamp=' + str(current_time)
            input_string = url_pre + api_secret
            sign = hashlib.md5(input_string.encode("utf8")).hexdigest()
            url = url +'?'+ url_pre + '&sign=' + sign
            logging.info("url is "+url)
            params={"osUUID":uuid,"code":info,"apiKey":api_key,"nonStr":nonStr,"timestamp":str(current_time),"sign":sign}
            response=requests.get(url=url,timeout=10)#,params=params)
            if response.content:
                res_json=response.json()
                logging.info(res_json)
                
            if res_json['code'] == 500 or not res_json['data']:
                logging.info("Could not get meta info '"+info+"' from http /api/metadata/get")
                if is_retry:
                    return None
                return
            else:
                return res_json['data'][info]
        except  KeyError as e:
            logging.info("Could not get meta info '"+info+"' from http /api/metadata/get")
            if is_retry:
                return None
            return
        except Exception as e:
            logging.info('getapi operation is failed')
            logging.info(e)
            return None

    def get_record_map(self,info_list):
        count=6
        while count > 0:
            try:
                meta_info=self.get_record_meta()
                url = meta_info['patch_host']+'/api/openApi/cdserv/api/metadata/realTime/getMap'
                # url = 'http://169.254.169.254/api/openApi/cdserv/api/metadata/realTime/getMap' # 测试异常用
                uuid = meta_info['uuid']
                api_key = '9f8b602b9d90314a24af41c11b459561'
                api_secret = '033d69ff3a6d6a2b2d14e5f7237e4166'
                nonStr = ''.join(random.sample(string.digits + string.ascii_letters,8))
                #logging.info(nonStr)
                current_time = int(time.time())
                info=",".join(info_list)
                url_pre = 'apiKey=' + api_key + '&codes=' + info + '&nonStr=' + nonStr + '&osUUID=' + uuid + '&timestamp=' + str(current_time)
                input_string = url_pre + api_secret
                sign = hashlib.md5(input_string.encode("utf8")).hexdigest()
                url = url +'?'+ url_pre + '&sign=' + sign
                logging.info("url is "+url)
                params={"osUUID":uuid,"code":info,"apiKey":api_key,"nonStr":nonStr,"timestamp":str(current_time),"sign":sign}
                response=requests.get(url=url,timeout=5)#,params=params)
                if response.content:
                    res_json=response.json()
                    logging.info(res_json)
                    
                if res_json['code'] == 0 :
                    return res_json['data']
                elif res_json['code'] != 0:
                    logging.info("Could not get meta info  '"+info+"' from http /api/metadata/getmap")
                    count=count-1
                    time.sleep(5)
                    continue
                    
            except Exception as e:
                logging.exception('getapi operation is failed')
                logging.info(e)
                count=count-1
                time.sleep(5)
                continue
                
    
    def get_record_dll(self,info):
        # 加载DLL
        dll_path = "C:\\Program Files\\Cloudbase Solutions\\Cloudbase-Init\\exe\\clinkapi.dll"  # 将 "./clinapi.dll" 替换为实际的DLL文件路径
        example_dll = ctypes.CDLL(dll_path)
        # 定义函数签名
        example_dll.clinkapiGetMetaData.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
        example_dll.clinkapiGetMetaData.restype = ctypes.c_int
        # 定义 valueSize 变量
        valueSize = 100  # 假设 valueSize 为 100，可以根据实际情况修改
        # 创建存储结果的缓冲区
        pValue = ctypes.create_string_buffer(b"", size=valueSize)
        # 其他参数
        key = info.encode('utf-8') # 替换为实际的 key
        appId = b"appId0002ecloudimgconfctyunexe24"  # 替换为实际的 appId
        appSecret = b"b37729d03183116cec097c6078d4d3db"  # 替换为实际的 appSecret
        # 构建 appAuthStr
        nonStr = ''.join(random.sample(string.ascii_letters + string.digits, k=8))
        timestamp = str(int(time.time()))
        signPre = "appId=" + appId.decode('utf-8') + "&nonStr=" + nonStr + "&timestamp=" + timestamp
        md5str = signPre + appSecret.decode('utf-8')
        md5 = hashlib.md5()
        md5.update(md5str.encode('utf-8'))
        sign = md5.hexdigest()
        appAuthStr = (signPre + "&sign=" + sign).encode('utf-8')  # 将 appAuthStr 转换为字节串
        logging.info("md5str:"+md5str)
        logging.info("sign:"+sign)
        logging.info("appAuthStr:"+str(appAuthStr, encoding='utf-8'))
        # 调用函数
        result = example_dll.clinkapiGetMetaData(pValue, valueSize, key, appId, appAuthStr)
        logging.info("result:"+str(result))
        if result == 0:
            meta_info=pValue.value.decode('utf-8')
            logging.info("meta info :"+str(meta_info))
            if meta_info:
                logging.info("Metadata retrieved successfully.")
                logging.info("Value:"+ meta_info)  # 将 pValue 转换为字符串并打印
                return meta_info
        logging.info("Failed to retrieve metadata.")
        return self.get_record_extend(info,False)

    def get_record_temp(self,info):
        with open('meta_data.json') as json_file:
            meta_json = json.load(json_file)
            meta_json = meta_json[info]
        return meta_json


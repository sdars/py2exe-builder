#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件  :ecloud_sfs_action.py
@说明  :挂载，卸载弹性文件系统
@时间  :2021/01/07 17:44:30
@作者  :dutianxing
@版本  :1.0
'''
import sys
sys.path.append(".")
from get_meta_data import GetMetaData
import logging,winreg,json,ctypes,string,os,time
from callpowershell import PowerShell
'''
logging.basicConfig(level = logging.DEBUG,
    format = '%(asctime)s %(levelname)-8s %(message)s', 
    datefmt = '%a, %d %b %Y %H:%M:%S',
    # C:\\Program Files\\Cloudbase Solutions\\Cloudbase-Init\\log
    filename = '.\\EIC.log',
    filemode = 'w')
console = logging.StreamHandler()
console.setLevel(logging.INFO) 
formatter = logging.Formatter('[%(levelname)-8s] %(message)s') #屏显实时查看，无需时间
console.setFormatter(formatter)
logging.getLogger().addHandler(console)
'''
class SFSAction():
    def mount_nfs(self,meta,has_signal):
        """挂载功能，通过has_signal参数判断为全局挂载或新增挂载
        Args:
            meta ([dict]]): 元数据
            has_signal (bool): 判断是否为信令触发，如果为True，则判断是否有新增磁盘待挂载；如果为False，则根据meta信息全部挂载
        """
        try:
            
            meta_list=list(filter(None,meta.strip('[]').split(',')))
            logging.info("meta code is ["+",".join(meta_list)+"]")    
        except KeyError:
            logging.info('Could not find the SFS url message from meta data.')
            return False
        # 判断信令，筛选待挂载列表
        if has_signal:
            reg_dict=self.get_reg_dict()
            wait_mouted_list=[]
            for url in meta_list:
                if url in reg_dict.values():
                    continue
                else:
                    wait_mouted_list.append(url)
        else:
            with PowerShell('GBK') as ps:
                out,err=ps.run("New-Item -Path 'HKLM:\SOFTWARE\ecloudsoft\Mirror\Cloudbase\SFS'")
            with PowerShell('GBK') as ps:
                out,err=ps.run("Remove-ItemProperty -Path 'HKLM:\SOFTWARE\ecloudsoft\Mirror\Cloudbase\SFS' -Name *")
                logging.info(out)
            wait_mouted_list=meta_list
        # 开始挂载
        args="["+",".join(wait_mouted_list)+"]"
        runcmd="start-process 'C:\Program Files\Cloudbase Solutions\Cloudbase-Init\exe\ecloud_do_mount.exe' '1 "+args+"'"
        logging.info(runcmd)
        with PowerShell('GBK') as ps:
            out,err=ps.run(runcmd)
        return True
        '''
        if self.do_mount(wait_mouted_list):
            return True
        else:
            return False'''
        
    def umount_nfs(self,meta):
        """[卸载功能，比对元数据和已存注册表，将元数据中没有的但注册表中存在的磁盘卸载]buz
        Args:
            meta ([dict]): [元数据]
        Returns:
            [bool]: [卸载结果]
        """
        try:
            # temp
            meta_list=meta.strip('[]').split(',')
            logging.info("meta code is ["+",".join(meta_list)+"]")    
        except KeyError:
            logging.info('Could not find the SFS url message from meta data.')
            return False
        reg_dict=self.get_reg_dict()
        wait_umounted_list=[]
        for url in reg_dict.items():
            if url[1] in meta_list:
                continue
            else:
                wait_umounted_list.append(url[0])
        logging.info("These disks are waiting to umount."+",".join(wait_umounted_list))
        # 开始卸载
        args="["+",".join(wait_umounted_list)+"]"
        runcmd="start-process 'C:\Program Files\Cloudbase Solutions\Cloudbase-Init\exe\ecloud_do_mount.exe' '0 "+args+"'"
        logging.info(runcmd)
        with PowerShell('GBK') as ps:
            out,err=ps.run(runcmd)
        return True
        '''
        if self.do_umount(wait_umounted_list):
            return True'''
        
    def change_capacity(self,url_list):
        return self.change_rights(url_list)
    
    def change_rights(self,url_list):
        """[弹性文件磁盘修改权限后，系统内需进行卸载并重新挂载操作]
        Args:
            url_list ([list]): [弹性文件地址列表]
        Returns:
            [bool]: [默认回复True]]
        """
        # 反转注册表字典，通过地址获取修改权限的盘符列表
        reg_dict_new= {v:k for k,v in self.get_reg_dict().items()}
        if reg_dict_new:
            logging.info("url list is "+url_list)
            wait_umounted_list=[]
            for url in url_list.strip('[]').split(','):
                wait_umounted_list.append(reg_dict_new.get(url))
            logging.info(str(wait_umounted_list))
            logging.info("These disks ["+",".join(wait_umounted_list)+"] rights have changed, they are going to umount and then mount now. ")
            #卸载修改权限的磁盘
            self.do_umount(wait_umounted_list)
            time.sleep(30)
        self.do_mount(url_list)
        return True
        
        
    def do_umount(self,wait_umounted_list):
        """[对收到的列表中的磁盘进行卸载操作]
        Args:
            wait_umounted_list ([string]): [盘符列表]
        Returns:
            [bool]: [卸载结果]
        """
        if len(wait_umounted_list):
            for disk_key in wait_umounted_list:
                logging.info("Now umount disk "+disk_key)
                umount_cmd="umount -f "+disk_key
                with os.popen(umount_cmd, "r") as p:
                    r = p.read()
                logging.info(r)
                with PowerShell('GBK') as ps:
                    out,err=ps.run("Remove-ItemProperty -Path 'HKLM:\SOFTWARE\ecloudsoft\Mirror\Cloudbase\SFS' -Name "+disk_key)
                    logging.info(out)
            return True
        else:
            logging.info("No more sfs url need to be umouted.")
            return False
        

    def do_mount(self,wait_mouted_list):
        """[挂载提供列表中的所有弹性系统]
        Args:
            wait_mouted_list ([string]): [弹性文件地址列表]
        Returns:
            [bool]: [挂载结果]
        """
        if len(wait_mouted_list):
            logging.info(len(wait_mouted_list))
            logging.info("Those url are waiting mouted: "+"||".join(wait_mouted_list) )    
            used_disklist=self.get_disklist()
            i=90
            for url in wait_mouted_list:
                # 从z开始获取未使用的盘符
                while True:
                    disk_num=str(chr(i))+":"
                    if disk_num in used_disklist:
                        i=i-1
                    else:
                        i=i-1
                        break
                mount_cmd="mount -o nolock "+url+" "+disk_num
                logging.info(mount_cmd)
                for i in range(3):
                    with os.popen(mount_cmd, "r") as p:
                        r = p.read()
                    logging.info(r)
                    temp_check = r.strip().split(":")
                    logging.info("&".join(temp_check))
                    if len(temp_check[0]) == 1:
                        logging.info("mount operation is succeed")
                        with PowerShell('GBK') as ps:
                            out,err=ps.run("Set-ItemProperty -Path 'HKLM:\SOFTWARE\ecloudsoft\Mirror\Cloudbase\SFS' -Name "+disk_num+" -Value "+url)
                        break
                    
                    logging.info("mount operation is failed. it will wait 30 second and retry.")
                    time.sleep(30)
                
                logging.info(out)
            return True
        else:
            logging.info("No more sfs url need to be mouted.")
            return False


    def get_reg_dict(self):
        """[获取注册表中保存的弹性文件挂载情况]
        Returns:
            [dict]: [存有挂载盘符和挂载地址的字典]
        """
        reg_dict={}
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r"SOFTWARE\ecloudsoft\Mirror\Cloudbase\SFS") 
            i = 0
             
            while 1: 
                #EnumValue方法用来枚举键值，EnumKey用来枚举子键
                name, value, type = winreg.EnumValue(key, i)
                logging.info(str(name)+"|"+str(value)+"|"+str(type))
                reg_dict[name]=value
                i += 1
        except WindowsError as e:
            pass
        
        logging.info(reg_dict)
        return reg_dict
    
    def get_disklist(self):
        """获取已使用盘符
        Returns:
            [list]: [盘符列表]
        """
        disk_list = []
        for c in string.ascii_uppercase:
            disk = c + ':'
            if os.path.isdir(disk):
                disk_list.append(disk)
        logging.info("These disks are alreday used : "+" ".join(disk_list))
        return disk_list
    
    def execute(self,commandId,url_list):
        logging.info("--------------------------------------------SFS-Action------------------------------------------------")
        meta=GetMetaData().get_record_extend('sfs_urls',False)
        if meta:
            if commandId == 1:
                logging.info("Action Id is 1, start mounting.")
                result=self.mount_nfs(meta,True)
            elif commandId == 2:
                logging.info("Action Id is 2, start umounting.")
                result=self.umount_nfs(meta)
            elif commandId == 3:
                logging.info("Action Id is 3, start change capacity ")
                result=self.change_capacity(url_list)
            elif commandId == 4:
                logging.info("Action Id is 4, no more actions in temp.")
                result=self.change_rights(url_list)
            else:
                logging.info("No action id, start mounting. ")
                result=self.mount_nfs(meta,False) #预留非信令拉起情况  
            return result 
        else:
            logging.info("Could not find sfs message in meta.")
            return False
'''
with open('meta_data.json') as json_file:
    meta_json = json.load(json_file)
    meta_json = meta_json['meta']
SFSAction().mount_nfs(meta_json,True)'''
#SFSAction().umount_nfs(meta_json)
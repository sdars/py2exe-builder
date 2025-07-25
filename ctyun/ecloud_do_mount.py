from callpowershell import PowerShell
import sys,time,os,subprocess,logging,string

logging.basicConfig(level = logging.DEBUG,
    format = '%(asctime)s %(levelname)-8s %(message)s', 
    datefmt = '%a, %d %b %Y %H:%M:%S',
    # C:\\Program Files\\Cloudbase Solutions\\Cloudbase-Init\\log
    filename = 'C:\\Program Files\\Cloudbase Solutions\\Cloudbase-Init\\log\\DM.log',
    filemode = 'w')
console = logging.StreamHandler()
console.setLevel(logging.INFO) 
formatter = logging.Formatter('[%(levelname)-8s] %(message)s') #屏显实时查看，无需时间
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

class DoMount():
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

pid=os.getpid()
cmdword="wmic process where(processid="+str(pid)+") get commandline /format:list"
try: 
    p=subprocess.Popen(cmdword, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE).stdout.read()
    args=str(p,encoding='utf-8').replace('\n', '').replace('\r', '').split( )  
    logging.info(args[0])  
    logging.info(args[1])   
    logging.info(args[2])   
    logging.info(args[3])   
    logging.info(args[4])
    logging.info(args[5])   
    logging.info(args[6])   
    logging.info(args[7])      
    temp = args.pop(-1)
    if temp.endswith(".py"):
        logging.info("未指定参数，")
    operate = args.pop(-2)
    logging.info(operate)
    logging.info(temp)
    wait_change_list=list(filter(None,temp.strip('[]').split(',')))
    logging.info(wait_change_list)
    if operate == "1":
        logging.info("开始挂载磁盘")
        DoMount().do_mount(wait_change_list)
        logging.info("开始卸载磁盘")
    if operate == "0":
        DoMount().do_umount(wait_change_list)
except Exception:
    # 无参数时运行以下组件
    pass
from callpowershell import PowerShell
import logging
import winreg

class CleanReg():
    def execute(self):
        logging.info("--------------------------start clean regedit trace-------------------------------------")
        logging.info("Clean cloudbase regedit............")
        with PowerShell('GBK') as ps:
            out,err=ps.run("stop-service -Name cloudbase-init -Force")  
            logging.info(out)
        with PowerShell('GBK') as ps:
            outs, errs = ps.run('Remove-Item "hklm:\software\cloudbase solutions\cloudbase-init"  -Force -Recurse')
            logging.info(outs)
        mirror_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\ecloudsoft\Mirror', 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(mirror_key, "NeedInitMachineInfo", 0, winreg.REG_DWORD, 1)


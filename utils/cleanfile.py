from callpowershell import PowerShell
import logging

class CleanFile():
    def execute(self):
        logging.info("--------------------------start clean file trace-------------------------------------")
        logging.info("Clean Temp File.................")
        with PowerShell('GBK') as ps:
            outs, errs = ps.run("Get-ChildItem $env:temp |   Remove-Item -Force -ErrorAction SilentlyContinue -Recurse")
            logging.info(outs)
        with PowerShell('GBK') as ps:
            outs, errs = ps.run("Get-ChildItem C:\\Windows\\Temp,c:\\temp |   Remove-Item -Force -ErrorAction SilentlyContinue -Recurse")
            logging.info(outs)
        logging.info("clean cloudbase-init log file..............")
        with PowerShell('GBK') as ps:
            outs, errs = ps.run("Get-ChildItem 'C:\\Program Files\\Cloudbase Solutions\\Cloudbase-Init\\log\\' |   Remove-Item -Force -ErrorAction SilentlyContinue -Recurse")
            logging.info(outs)
            logging.info("clean ctyun log file..............")
        with PowerShell('GBK') as ps:
            outs, errs = ps.run("Get-ChildItem 'C:\\Users\\Public\\Documents\\mirror' |   Remove-Item -Force -ErrorAction SilentlyContinue -Recurse")
            logging.info(outs)
        logging.info("clean recycle bin......................")
        with PowerShell('GBK') as ps:
            outs, errs = ps.run("Clear-RecycleBin -DriveLetter C -Force")
            logging.info(outs)
        with PowerShell('GBK') as ps:
            outs, errs = ps.run("gci C:\`$recycle.bin -force | remove-item -recurse -force")
            logging.info(outs)
        logging.info("clean the recent file open info..............")
        with PowerShell('GBK') as ps:
            outs, errs = ps.run("Get-ChildItem $env:appdata\Microsoft\Windows\Recent | Remove-Item -Force -ErrorAction SilentlyContinue -Recurse")
            logging.info(outs)
        with PowerShell('GBK') as ps: # 兼容win7 和 2008
            outs, errs = ps.run("Get-ChildItem $env:appdata\Microsoft\Windows\最近访问的项目 | Remove-Item -Force -ErrorAction SilentlyContinue -Recurse")
            logging.info(outs)
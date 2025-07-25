from callpowershell import PowerShell
import logging,time,os

class CleanExplorer():
    def execute(self):
        logging.info("--------------------------start clean explorer trace-------------------------------------")
        logging.info("Clean IE offline  favorites and download history.................")
        # time.sleep(5)
        with PowerShell('GBK') as ps:
            outs, errs = ps.run("RunDll32.exe InetCpl.cpl,ClearMyTracksByProcess 8")
            logging.info(outs)
        # time.sleep(5)
        logging.info("Clean Internet Temporary  Internet Files folder.................")
        with PowerShell('GBK') as ps:
            outs, errs = ps.run("RunDll32.exe InetCpl.cpl,ClearMyTracksByProcess 4")
            logging.info(outs)
        # time.sleep(5)
        with PowerShell('GBK') as ps:
            outs, errs = ps.run("$env:username")
            logging.info(outs)
        username=outs.strip()
        logging.info("Clean Internet browsing history ........")
        path='C:\\Users\\'+username+'\\AppData\\Local\\Microsoft\\Windows\\History\\'
        logging.info(path)
        with PowerShell('GBK') as ps:
            outs, errs = ps.run("test-path "+path)
        if outs.strip()=="True":
            with PowerShell('GBK') as ps:
                outs, errs = ps.run("Remove-Item "+path+" -Recurse -Force")
                logging.info(outs)
                logging.info(errs)
            with PowerShell('GBK') as ps:
                outs, errs = ps.run("New-Item -Path 'C:\\Users\\"+username+"\\AppData\\Local\\Microsoft\\Windows' -name History -type directory -Force")
                logging.info(outs)
                logging.info(errs)
        logging.info("Repair Internet browsing history ........")
        '''with PowerShell('GBK') as ps:
            outs, errs = ps.run("Start-Process -FilePath 'C:\\WINDOWS\\system32\\attrib.exe' -ArgumentList '+s C:\\Users\\"+username+"\\AppData\\Local\\Microsoft\\Windows\\History'")
        '''
        temp=os.path.expandvars(r'%USERPROFILE%\AppData\Local\Microsoft\Windows\History')
        os.system("attrib +s "+temp)
        logging.info(temp)
        # time.sleep(5)
        
import sys
import os
import time
#import threading
import shutil
from termcolor import colored
import ComputeHash
import traceback

#import Malbox
#import VMControl
import VMControl_rev
import subprocess
import ConfigParser

local_path = os.getcwd()
config_file = os.getcwd() + '/config.ini'
LOG_FILE = os.getcwd() + '/malbox_log.log'
cf = ConfigParser.ConfigParser()
cf.read(config_file)
UPLOAD_PATH = cf.get('ListenerConf','upload_path')
REPORT_PATH = cf.get('ListenerConf','report_path')
TEMP_PATH = cf.get('ListenerConf', 'temp_path')
VM_PAUSE = int(cf.get('ListenerConf','vm_pause'))

ANALYZE_TIMEOUT = 150
VM_INDEX = ''

BAD_FILE_LIST=[]

print "start here..."
if not os.path.exists(UPLOAD_PATH):
    os.makedirs(UPLOAD_PATH)       
    
'''
class malbox_thread(threading.Thread):
    def __init__(self,filename):
        threading.Thread.__init__(self)
        self.filename = filename
    def run(self):
        print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        Malbox.AnalyzeFile(self.filename)
'''        

def PrintColored(info,color='white'):
    if sys.platform.startswith('win'):
        print info
    else:
        print colored(info,color)
     
def MalboxListen():
    #waiting = False
    vs=VMControl_rev.conn("admin","Password123!@#")
    while True:
        time.sleep(2)
        try:
            #fetch file
            contents = os.listdir(UPLOAD_PATH)            
            files = []
            for content in contents:
                if os.path.isfile(UPLOAD_PATH+content):
                    files.append(UPLOAD_PATH+content)            
            '''
            for f in files:
                if f in BAD_FILE_LIST:
                    files.remove(f)
            '''
            if len(files)==0:
                print "no files were found in " + str(UPLOAD_PATH)  #added by johnson 2013-04-11
                print "sleep 10sec then retry ..."
                time.sleep(10) 
                print "exit ... L73"
                exit()          
                continue
                      
            while len(files):
                
                #well, we have to get some idle vms first :)
                while True:
                    IdleVmList=vs.getIdleVmList()
                    if IdleVmList:
                        break
                    else:
                        print "no idle vms, so wait for it ..."
                        time.sleep(5)
            
                print "you are so lucky, we have idle vms ..."        
                print str(IdleVmList)

                while True:
                    if not len(files):
                        break
                    if not len(IdleVmList):
                        break
                    upload_file = files[0]
                    vm_path=IdleVmList[0]
                    print str(vm_path) 
                    del files[0]     
                    del IdleVmList[0]      
                    md5 = ComputeHash.md5sum(upload_file)          
                    PrintColored('fetch file:%s,%s' %(upload_file,md5),'green')
                    report_file = REPORT_PATH + md5 + '.html'   
                             
                    if os.path.isfile(report_file):
                        PrintColored('report exsits already','green')
                        try:
                            #os.remove(upload_file)
                            print "nothing todo..."
                        except:
                            BAD_FILE_LIST.append(upload_file)
                        continue
        
                    VM_INDEX = 0
                  
                    extension = 'exe'
                    try:
                        extension = upload_file[upload_file.rindex('.')+1:]
                    except:
                        pass
                    temp_file = TEMP_PATH + 'sample%s.%s' % (md5,extension)
                    
                    if not os.path.exists(TEMP_PATH):
                        os.makedirs(TEMP_PATH)            
                   
                    if os.path.isfile(upload_file):
                        if os.path.isfile(temp_file):
                            os.remove(temp_file)
                        shutil.copyfile(upload_file,temp_file)
                        os.remove(upload_file)
                    
                        #analyze with malbox.py
                        #thread = malbox_thread(temp_file)
                        #thread.setDaemon(True)
                        #thread.start()                
                        #thread.join(ANALYZE_TIMEOUT)
                    print "will call CallMalbox(...)"
                    CallMalbox(temp_file,VM_INDEX,vm_path)
                    
                time.sleep(20)
            
            print "done, exit ..."    
            exit() 
                
            '''    
                #time.sleep(VM_PAUSE)
                    #send mail
                    #if not (email=='' or email==None):
                    #    SendMail(email,file,report_file)
                    #os.remove(upload_file)
                try:
                    #os.remove(upload_file)
                    print "nothing todo L138"
                except:
                    BAD_FILE_LIST.append(upload_file)
                else:
                    PrintColored('file not exists ...L142','red')               
            '''
            #exit()    
               
        except Exception,e :
            print e
            print traceback.format_exc()
        
        #print 'Analysis Done!'
        PrintColored('Analysis Done','green')
    
   

def CallMalbox(filename,vm_index,vm_path):
    malbox_path = sys.path[0] + '\\' + 'MalBox.py'
    if os.path.isfile(malbox_path):        
        command = 'python "%s" "%s" %s "%s"' %(malbox_path,filename,vm_index,vm_path)
    else:
        malbox_path = local_path + '\\Malbox.exe'
        command = '"%s" "%s" %s "%s"' %(malbox_path,filename,vm_index,vm_path)
    print command
    #pipe = os.popen(command)
    os.chdir(local_path)
    subprocess.Popen(command,shell=True)
    os.chdir(os.path.abspath(os.path.join(os.getcwd(),os.path.dirname(__file__))))


        
if __name__ == '__main__':   
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    PrintColored('Malbox start listening...','green')
    MalboxListen()
    
    

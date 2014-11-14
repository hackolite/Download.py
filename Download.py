import urllib2
import threading
import os
import sys 
 
class FileDownloader(threading.Thread):
 
    
    def __init__(self,workQueue, queueLock, count, url):
        self.url = url
        self.progress = None
        self.status = None # {0:"Downloading", 1:"Completed", 2:"Paused", 3:"Error"}
        self.fileName = None
        self.u = None
        self.fileSize = None
        self.szDownloaded = 0
        self.isPaused = False
        super(FileDownloader, self).__init__()   # super() will call Thread.__init__ for you
        self.workQueue = workQueue
        self.queueLock= queueLock
        super(FileDownloader, self).__init__()   # super() will call Thread.__init__ for you
        self.workQueue = workQueue
        self.queueLock= queueLock

    def run(self,start=None):
        start = 0

        proxy = urllib2.ProxyHandler({'https':'https://****************:***'})
        auth = urllib2.HTTPBasicAuthHandler()
        opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
        urllib2.install_opener(opener)
        req = urllib2.Request(self.url)
    
        self.u = urllib2.urlopen(req)
        print self.u.getcode()
        self.fileSize = int(self.u.headers['content-length'])
        print "header", self.fileSize
        req.headers["Range"] = "bytes=%s-%s" %(start, self.fileSize)

        self.fileName = self.url.split("/")[-1]

        self.state = 1     
        if not os.path.isfile("./ab.tmp"):
            print "pas de fichier temporaire le telechargement va demarrer"
            f = open("ab.tmp", 'ab')
            self.fileSize = int(self.u.headers['content-length'])
            

            block_sz = 8192
            while (self.state == 1):
                buffer = self.u.read(block_sz)
                if not buffer:
                    print "telechargement termine"
                    self.state  = 0
                self.szDownloaded += len(buffer)
                f.write(buffer)
                print(self.szDownloaded)
            
            
            if  self.workQueue.get() == 'pause':
                f.close()               
                state=0            
                print 'mise en pause'
                sys.exit(0)                
            
                if  self.workQueue.get() == 'resume':
                        state=1
                  
        
                if  self.workQueue.get() == 'start':
                    state=1                   
                    os.rename("./ab.tmp",self.fileName)
            else:
                print "un fichier temporaire a ete trouve, le telechargement demarre a partir de"
                f = open("ab.tmp", 'ab')
                self.fileSize = int(self.u.headers['content-length'])
                req_tmp = urllib2.Request(self.url)
                print req_tmp
                req_tmp.add_header('Range', 'bytes=' + str(6000000) + '-' + str(self.fileSize))               
                print req_tmp.headers["Range"]
                
                self.u_tmp = urllib2.urlopen(req_tmp)
                print "code retour server", self.u_tmp.getcode()
                block_sz = 8192
                while (self.state == 1):
                    buffer = self.u_tmp.read(block_sz)
                    if not buffer:         
                        print "telechargement termine"
                        sys.exit(0)
                    self.szDownloaded += len(buffer)
                    f.write(buffer)
                    print "completing download",self.szDownloaded

 
    def pauseDownload(self):
        self.isPaused = True
        print "downloading is pause"
        #save a file with the download status, then I'll be able to resume it
 
    def resumeDownload(self):
           pass        

import threading
import Queue
import time

work_q = Queue.Queue()     # first create your "work object"
q_lock = threading.Lock()
count = 1
myurl = "https://ia802508.us.archive.org/5/items/testmp3testfile/mpthreetest.mp3"
FileDownloader = FileDownloader(work_q, q_lock, count,myurl)  # after instantiate like this your Thread
FileDownloader.setDaemon(True)
FileDownloader.start()
with q_lock:
    work_q.put('pause')
FileDownloader.join()

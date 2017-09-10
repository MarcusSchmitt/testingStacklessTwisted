import stackless
from multiprocessing import Process, Manager, Queue
from queue import Empty
from threading import Thread, Lock
from datetime import date, datetime, timedelta
import time
from General.basicFunctions import keepAlive
import myStackless

class StacklessProcess(object):
    '''Use this class for everything related to multiprocessing Process. Alter code if need be.'''
    def __init__(self, target, lock, args=(), listenChannel=None, responseChannel=None):
        self.target = target
        self.lock = lock
        self.args = args
        self.listenChannel = listenChannel
        self.responseChannel = responseChannel
        self.listenQueue = Queue()
        self.responseQueue = Queue()
        self.finishQueue = Queue()

    def start(self):
        #self.lock.acquire()
        existingThreads = len(stackless.threads)
        #self.process = Process(target=dummySpawner, args=(self.target, existingThreads, self.queue, self.args))
        #self.process = Process(target=self.target, args=(self.target, list(self.args), self.responseChannel,
                                                        #self.responseQueue, self.listenChannel, self.listenQueue,
                                                        #self.finishQueue, existingThreads))
        self.process = Process(target=self.target, args=self.args)
        self.process.start()
        if self.listenChannel is not None:
            myStackless.tasklet(forwardChannelToQueue)(self.listenChannel, self.listenQueue, 'MainThread lC')
        if self.responseChannel is not None:
            myStackless.tasklet(forwardQueueToChannel)(self.responseChannel, self.responseQueue, 'MainThread rC')
        #self.lock.release()
        #message = self.finishQueue.get()
        #if message == "DONE":
            #print("LOCK RELEASED")
            #self.lock.release()
        #else:
            #print("SOMETHING WENT WRONG")


def getLock():
    return Lock()

def testListening(lC, rC):
    while True:
        message = lC.receive()
        rC.send(message)

def testSending(rC):
    while True:
        message = rC.receive()
        print(message)

def testChannelConnection(lC, rC):
    myStackless.tasklet(testListening)(lC, rC)

def delayedStart(p):
    init = datetime.now() + timedelta(seconds=1)
    while datetime.now() < init:
        stackless.schedule()
    p.start()

def stackStart(p):
    p.start()

def printCall(message):
    print(message)
    while True:
        time.sleep(1)
        print(message, datetime.now())
        stackless.schedule()

def stackPrint(message, taskletList):
    mainTasklet = stackless.getmain()
    count = stackless.getruncount()
    currentTasklet = stackless.getcurrent()
    for key in list(taskletList.keys()):
        taskletList[key].killComplete()
    #try:
        #print(mainTasklet.next)
        #print(mainTasklet.next())
    #except Exception:
        #pass
    #for i in range(count - 1):
        #nextTasklet = currentTasklet.next()
        #if not nextTasklet.is_main or currentTasklet == nextTasklet:
            #print("Destroy current", nextTasklet)
            #nextTasklet.kill()
            #nextTasklet.remove()
    print(stackless.runcount)
    myStackless.tasklet(keepAlive)()
    myStackless.tasklet(printCall)(message)
    stackless.run()

if __name__ == '__main__':
    lock = getLock()
    taskletList = []
    mainTasklet = stackless.getmain()
    myStackless.tasklet(keepAlive)()
    taskletList.append(myStackless.tasklet(printCall))
    taskletList[-1]("MainThread still running")
    taskletList.append(myStackless.tasklet(printCall))
    taskletList[-1]("MainThread still running2")
    taskletList.append(myStackless.tasklet(printCall))
    taskletList[-1]("MainThread still running3")
    taskletList.append(myStackless.tasklet(printCall))
    taskletList[-1]("MainThread still running4")
    p1 = StacklessProcess(target=stackPrint, lock=lock, args=("P1 still running", myStackless.allTasklets))
    myStackless.tasklet(stackStart)(p1)
    p2= StacklessProcess(target=stackPrint, lock=lock, args=("P2 still running", myStackless.allTasklets))
    myStackless.tasklet(stackStart)(p2)
    p3 = StacklessProcess(target=stackPrint, lock=lock, args=("P3 still running", myStackless.allTasklets))
    myStackless.tasklet(stackStart)(p3)
    #import pdb; pdb.set_trace()
    stackless.run()
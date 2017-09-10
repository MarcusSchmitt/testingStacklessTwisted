import stackless
from multiprocessing import Process, Manager, Queue
from queue import Empty
from threading import Thread, Lock
from datetime import date, datetime, timedelta
import time



def getSharedObjects():
    mgr = Manager()
    return mgr, mgr.dict(), mgr.list()


def getLock():
    return Lock()

def dummyLoop():
    #print(stackless.threads)
    while True:
        time.sleep(1000)
        stackless.schedule()

def dummyThread():
    stackless.tasklet(dummyLoop)()
    stackless.run()

def dummyResponse(channel):
    while True:
        print("Send On Channel: ", channel)
        channel.send(True)
        for i in range(1000000):
            stackless.schedule()
def dummyResponseQ(queue):
    while True:
        print("Send On Queue: ", queue)
        queue.put(True)
        for i in range(1000000):
            stackless.schedule()

def trueLaunch(target, args, rC, rQ, lC, lQ):
    print("start new thread")
    if rC is not None:
        rC = stackless.channel()
        stackless.tasklet(forwardChannelToQueue)(rC, rQ, 'NewProcess rC')
    if lC is not None:
        lC = stackless.channel()
        stackless.tasklet(forwardQueueToChannel)(lC, lQ, 'NewProcess lC')
    args.append(lC)
    args.append(rC)
    #stackless.tasklet(target)(*args)
    target(*args)
    stackless.tasklet(dummyLoop)()
    print(stackless.threads)
    stackless.tasklet(dummyResponse)(rC)
    stackless.tasklet(dummyResponseQ)(rQ)
    stackless.run()
    print("Thread stopped running")

def forwardChannelToQueue(channel, queue, identifier=""):
    print("Forward Channel To Queue -{0} -".format(identifier), channel, queue)
    while True:
        message = channel.receive()
        print("received message on CHANNEL -{0} -".format(identifier), message)
        queue.put(message)

def forwardQueueToChannel(channel, queue, identifier=""):
    print("Forward Queue To Channel -{0} -".format(identifier), queue, channel)
    while True:
        try:
            message = queue.get(block=False)
            print("received message on QUEUE -{0} -".format(identifier), message)
            channel.send(message)
        except Empty:
            #print("ErrorCheck")
            for i in range(100000):
                stackless.schedule()


def spawnMain(target, args, rC, rQ, lC, lQ, fQ, count):
    killThose = list()
    for i in range(count-1):
        killThose.append(Thread(target=dummyLoop, args=()))
        killThose[-1].start()
    t = Thread(target=trueLaunch, args=(target, args, rC, rQ, lC, lQ))
    t.start()
    fQ.put("DONE")
    #stackless.tasklet(dummyLoop)()
    #stackless.run()


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
        self.lock.acquire()
        existingThreads = len(stackless.threads)
        #self.process = Process(target=dummySpawner, args=(self.target, existingThreads, self.queue, self.args))
        self.process = Process(target=spawnMain, args=(self.target, list(self.args), self.responseChannel,
                                                        self.responseQueue, self.listenChannel, self.listenQueue,
                                                        self.finishQueue, existingThreads))
        #self.process = Process(target=self.target, args=self.args)
        self.process.start()
        if self.listenChannel is not None:
            stackless.tasklet(forwardChannelToQueue)(self.listenChannel, self.listenQueue, 'MainThread lC')
        if self.responseChannel is not None:
            stackless.tasklet(forwardQueueToChannel)(self.responseChannel, self.responseQueue, 'MainThread rC')
        #self.lock.release()
        message = self.finishQueue.get()
        if message == "DONE":
            print("LOCK RELEASED")
            self.lock.release()
        else:
            print("SOMETHING WENT WRONG")

def testListening(lC, rC):
    while True:
        message = lC.receive()
        rC.send(message)

def testSending(rC):
    while True:
        message = rC.receive()
        print(message)

def testChannelConnection(lC, rC):
    stackless.tasklet(testListening)(lC, rC)

def delayedStart(p):
    init = datetime.now() + timedelta(seconds=5)
    while datetime.now() < init:
        stackless.schedule()
    p.start()

if __name__ == '__main__':
    from basicFunctions import stacklessTicker, keepAlive
    lock = getLock()
    lC = stackless.channel()
    rC = stackless.channel()
    #stackless.tasklet(stacklessTicker)(lC, 100000, date(3521, 5, 15))
    stackless.tasklet(keepAlive)()
    stackless.tasklet(testSending)(rC)
    stackless.tasklet(dummyResponse)(lC)
    p = StacklessProcess(target=testChannelConnection, lock=lock, args=(), listenChannel=lC, responseChannel=rC)
    stackless.tasklet(delayedStart)(p)
    stackless.run()
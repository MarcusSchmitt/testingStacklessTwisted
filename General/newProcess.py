import stackless
from multiprocessing import Process, Manager, Queue
from threading import Thread, Lock
import socket, time
from datetime import datetime, timedelta


def getSharedObjects():
    mgr = Manager()
    return mgr, mgr.dict(), mgr.list()


def getLock():
    return Lock()

def dummyLoop():
    #print(stackless.threads)
    while True:
        stackless.schedule()

def trueLaunch(target, args):
    target(*args)
    stackless.tasklet(dummyLoop)()
    stackless.run()

def forwardChannelToQueue(channel, queue):
    while True:
        message = channel.receive()
        queue.put(message)

def forwardQueueToChannel(channel, queue):
    while True:
        message = queue.get()
        channel.send(message)

def dummySpawner(target, count, queue, args):
    killThose = list()
    for i in range(count-1):
        killThose.append(Thread(target=dummyLoop, args=()))
        killThose[-1].start()
    t = Thread(target=trueLaunch, args=(target, args))
    t.start()
    queue.put("DONE")

def spawnMain(target, args, rC, rQ, lC, lQ, fQ, count):
    killThose = list()
    for i in range(count-1):
        killThose.append(Thread(target=dummyLoop, args=()))
        killThose[-1].start()
    t = Thread(target=trueLaunch, args=(target, args))
    t.start()
    if rC is not None:
        stackless.tasklet(forwardChannelToQueue)(rC, rQ)
    if lC is not None:
        stackless.tasklet(forwardQueueToChannel)(lC, lQ)
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
        self.process = Process(target=spawnMain, args=(self.target, self.args, self.responseChannel,
                                                        self.responseQueue, self.listenChannel, self.listenQueue,
                                                        self.finishQueue, existingThreads))
        #self.process = Process(target=self.target, args=self.args)
        self.process.start()
        if self.listenChannel is not None:
            stackless.tasklet(forwardChannelToQueue)(self.listenChannel, self.listenQueue)
        if self.responseChannel is not None:
            stackless.tasklet(forwardQueueToChannel)(self.responseChannel, self.responseQueue)
        #self.lock.release()
        message = self.finishQueue.get()
        if message == "DONE":
            print("LOCK RELEASED")
            self.lock.release()
        else:
            print("SOMETHING WENT WRONG")
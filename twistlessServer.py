import stackless
import time
from datetime import datetime, timedelta
import sys
from twisted.internet import reactor, task
from twisted.internet.protocol import Protocol, Factory
from multiprocessing import Process, Queue, Manager
from separateProcess import makeProcess
from mpt2 import makeMulti

#def setupGlobals():
    #global reactor_tasklet, subtasklets, twistedStacklessChannel, tickerChannel, threadChannel, connectionDict, mainQue, sharedDict
    #reactor_tasklet = None
    #tickerChannel = stackless.channel()
    #threadChannel = stackless.channel()
    #mainQue = Queue()
    #manager = Manager()
    #sharedDict = manager.dict()
reactor_tasklet = None

#twisted parts - protocoll and network related stuff
class Tcp(Protocol):
    def __init__(self, connectionDict, subtasklets, shutDown):
        self.connectionDict = connectionDict
        self.subtasklets = subtasklets
        self.shutDown = shutDown

    def dataReceived(self, data):
        #deferred callback for Twisted - called whenever data is received via network protocolls
        print('data received: ', data)

    def sendMessage(self, data):
        #function to send messages to connected clients
        self.transport.write(str(data).encode("utf-8"))

    def connectionMade(self):
        # Want to only transport message when I command not immediately when connected
        self.connectionDict[self] = self
        print("Connection Made")

    def connectionLost(self, reason):
        self.shutDown(self.subtasklets)

class TcpFactory(Factory):
    def __init__(self, connectionDict, subtasklets, shutDown):
        self.connectionDict = connectionDict
        self.subtasklets = subtasklets
        self.shutDown = shutDown

    def buildProtocol(self, addr):
        connection = Tcp(self.connectionDict, self.subtasklets, self.shutDown)
        return connection


def shutDown():
    reactor.stop()
    #mainQue.put("KILL")
    for ts in subtasklets:
        if ts is not None:
            ts.kill()


def listenToChannel(threadChannel, connectionDict):
    while True:
        message = threadChannel.receive()
        if message == "DONE":
            for key, connection in connectionDict.items():
                try:
                    connection.sendMessage(tickerChannel.receive())
                except AttributeError:
                    pass


def reactor_run(connectionDict, subtasklets):
    #import pdb; pdb.set_trace()
    global reactor_tasklet
    if reactor_tasklet is None:
        print("Setup Reactor")
        reactor_tasklet = stackless.getcurrent()
        #repeatedly call stackless.schedule
        schedulingTask = task.LoopingCall(stackless.schedule)
        #this prevents the reactor from blocking out the other tasklets
        factory = TcpFactory(connectionDict, subtasklets, shutDown)
        reactor.listenTCP(8001, factory)
        print("Setup Scheduler")
        schedulingTask.start(0.0001)
        print("Start Reactor")
        reactor.run()


def stacklessTicker(channel, tickTime):
    initTime = datetime.now()
    tickTime = timedelta(microseconds=tickTime)
    nextTime = initTime  + tickTime
    lastTime = nextTime + timedelta(seconds=15)
    while (1):
        while datetime.now() < nextTime:
            stackless.schedule()
        nextTime += tickTime
        if nextTime > lastTime:
            sys.exit()
        value = str(datetime.now()-initTime)
        channel.send(value)

if __name__ == '__main__':
    print("Execute Main")
    tickerChannel = stackless.channel()
    threadChannel = stackless.channel()
    mainQue = Queue()
    manager = Manager()
    sharedDict = manager.dict()
    connectionDict = dict()
    subtasklets = list()
    #setupGlobals()
    subtasklets.append(stackless.tasklet(makeProcess))
    #subtasklets[-1]()
    subtasklets[-1](mainQue, tickerChannel, threadChannel, sharedDict)
    stackless.tasklet(reactor_run)(connectionDict, subtasklets)
    subtasklets.append(stackless.tasklet(listenToChannel))
    subtasklets[-1](threadChannel, connectionDict)
    subtasklets.append(stackless.tasklet(stacklessTicker))
    subtasklets[-1](tickerChannel, 100000)
    stackless.run()
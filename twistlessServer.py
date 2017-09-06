import stackless
import time
import sys
from twisted.internet import reactor, task
from twisted.internet.protocol import Protocol, Factory
from multiprocessing import Process, Queue
 
reactor_tasklet = None
subtasklets = list()
twistedStacklessChannel = stackless.channel()
tickerChannel = stackless.channel()
threadChannel = stackless.channel()
connectionDict = {}
mainQue = Queue()
#twisted parts - protocoll and network related stuff
class Tcp(Protocol):
    def dataReceived(self, data):
        #deferred callback for Twisted - called whenever data is received via network protocolls
        print('data received: ', data)
        
    def sendMessage(self, data):
        #function to send messages to connected clients
        self.transport.write(str(data).encode("utf-8"))

    def connectionMade(self):
        # Want to only transport message when I command not immediately when connected
        connectionDict[self] = self
        print("Connection Made")
    
    def connectionLost(self, reason):
        shutDown()

class TcpFactory(Factory):
    def buildProtocol(self, addr):
        connection = Tcp()
        return connection


def shutDown():
    reactor.stop()
    mainQue.put("KILL")
    for ts in subtasklets:
        if ts is not None:
            ts.kill()


def listenToChannel():
    while True:
        data = threadChannel.receive()
        for key, connection in connectionDict.items():
            try:
                print(data)
                connection.sendMessage(data)
            except AttributeError:
                pass


def makeProcess():
    import separateProcess as sP
    solSyst = Process(target=sP.run, args=(mainQue,))
    solSyst.start()
    while True:
        tickerChannel.receive()
        mainQue.put("UPDATE")
        update = mainQue.get()
        threadChannel.send(update)
    

def reactor_run( ):
    print("Setup Reactor")
    reactor_tasklet = stackless.getcurrent()
    #repeatedly call stackless.schedule
    schedulingTask = task.LoopingCall(stackless.schedule)
    #this prevents the reactor from blocking out the other tasklets
    factory = TcpFactory()
    reactor.listenTCP(8001, factory)
    print("Setup Scheduler")
    schedulingTask.start(0.0001)
    print("Start Reactor")
    reactor.run()


def stacklessTicker(channel, tickTime):
    nextTime = time.clock() + tickTime
    while (1):
        while time.clock() < nextTime:
            stackless.schedule()
        nextTime += tickTime
        if nextTime > 10:
            sys.exit()
        print(time.clock())
        channel.send(time.clock())

if __name__ == '__main__':
    stackless.tasklet(reactor_run)()
    #subtasklets.append(stackless.tasklet(listenToChannel))
    #subtasklets[-1]()
    stackless.tasklet(listenToChannel)()
    #subtasklets.append(stackless.tasklet(stacklessTicker))
    #subtasklets[-1](tickerChannel, 0.1)
    stackless.tasklet(stacklessTicker)(tickerChannel, 0.1)
    #subtasklets.append(stackless.tasklet(makeProcess))
    #subtasklets[-1]()
    #stackless.tasklet(makeProcess)()
    stackless.run()
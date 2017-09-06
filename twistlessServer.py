import stackless
import time
import sys
from twisted.internet import reactor, task
from twisted.internet.protocol import Protocol, Factory
 
reactor_tasklet = None
mainChannel = stackless.channel()
listener = None
ticker = None
connectionDict = {}
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
    if reactor_tasklet is not None:
        reactor_tasklet.kill()
    if listener is not None:
        listener.kill()
    if ticker is not None:
        ticker.kill()


def listenToChannel():
    while True:
        data = mainChannel.receive()
        for key, connection in connectionDict.items():
            try:
                connection.sendMessage(data)
            except AttributeError:
                pass


def reactor_run( ):
    print("Setup Reactor")
    reactor_tasklet = stackless.getcurrent()
    #repeatedly call stackless.schedule
    schedulingTask = task.LoopingCall(stackless.schedule)
    #this prevents the reactor from blocking out the other tasklets
    factory = TcpFactory()
    global listener, ticker
    listener = stackless.tasklet(listenToChannel)()
    ticker = stackless.tasklet(stacklessTicker)(mainChannel, 0.5)
    reactor.listenTCP(8000, factory)
    print("Setup Scheduler")
    schedulingTask.start(0.000001)
    print("Start Reactor")
    reactor.run()


def stacklessTicker(channel, tickTime):
    nextTime = time.clock() + tickTime
    while (1):
        while time.clock() < nextTime:
            stackless.schedule()
        nextTime += tickTime
        if nextTime > 15:
            sys.exit()
        channel.send(time.clock())


stackless.tasklet(reactor_run)()
stackless.run()
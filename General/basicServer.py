import stackless
import time
from datetime import datetime, timedelta
import sys
from twisted.internet import reactor, task
from twisted.internet.protocol import Protocol, Factory
from multiprocessing import Process, Queue, Manager


reactor_tasklet = None

#twisted parts - protocoll and network related stuff
class Tcp(Protocol):
    def __init__(self, connectionDict, shutDown):
        self.connectionDict = connectionDict
        #self.subtasklets = subtasklets
        self.shutDown = shutDown

    def dataReceived(self, data):
        #deferred callback for Twisted - called whenever data is received via network protocolls
        print('data received: ', data)

    def sendMessage(self, data):
        #function to send messages to connected clients
        print("Trying to send message")
        self.transport.write(str(data).encode("utf-8"))

    def connectionMade(self):
        # Want to only transport message when I command not immediately when connected
        self.connectionDict[self] = self
        print("Connection Made")

    def connectionLost(self, reason):
        self.shutDown()

class TcpFactory(Factory):
    def __init__(self, connectionDict, shutDown):
        self.connectionDict = connectionDict
        #self.subtasklets = subtasklets
        self.shutDown = shutDown

    def buildProtocol(self, addr):
        connection = Tcp(self.connectionDict, self.shutDown)
        return connection


class CommunicationServer(object):
    def __init__(self, port, responseChannel):
        self.responseChannel = responseChannel
        self.mainQue = Queue()
        self.manager = Manager()
        self.sharedDict = self.manager.dict()
        self.connectionDict = dict()
        self.subtasklets = list()
        self.port = port

    def run(self):
        #repeatedly call stackless.schedule
        schedulingTask = task.LoopingCall(stackless.schedule)
        #this prevents the reactor from blocking out the other tasklets
        factory = TcpFactory(self.connectionDict, self.shutDown)
        reactor.listenTCP(self.port, factory)
        print("Setup Scheduler")
        stackless.tasklet(self.respond)()
        schedulingTask.start(0.001)
        print("Start Reactor")
        reactor.run()
    
    def respond(self):
        while True:
            print("Init ResponseCheck Loop")
            message = self.responseChannel.receive()
            print("Received Message On RESPONSECHANNEL")
            for key, connection in self.connectionDict.items():
                connection.sendMessage(message)

    def shutDown(self):
        reactor.stop()
        #mainQue.put("KILL")
        for ts in self.subtasklets:
            if ts is not None:
                ts.kill()


if __name__ == '__main__':
    print("Execute Main")
    server = CommunicationServer(8001)
    server.run()
    stackless.run()
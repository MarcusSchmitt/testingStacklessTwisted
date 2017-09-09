import stackless
import time
from mpt2 import makeMulti, makeMulti2
#from multiprocessing import Manager
from twisted.internet import reactor, task
from twisted.internet.protocol import Protocol, Factory
from threading import Lock

def third():
    print("Function Third")
    while True:
        time.sleep(1)
        stackless.schedule()


def fourth():
    print("Function Fourth")
    while True:
        time.sleep(1)
        stackless.schedule()


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


def fifth():
    print("Fifth")
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


if __name__ == '__main__':
    mainLock = Lock()
    stackless.tasklet(fifth)()
    stackless.tasklet(third)()
    stackless.tasklet(fourth)()
    stackless.tasklet(makeMulti)(mainLock)
    stackless.tasklet(makeMulti2)(mainLock)
    #import pdb; pdb.set_trace()
    print(stackless.getruncount() ,stackless.getthreads())
    stackless.run()
import stackless
from datetime import date, timedelta, datetime
from General.outsourcingTask import generateSol, stacklessTicker
from General.basicServer import CommunicationServer
from General.newProcess import StacklessProcess, getLock, getSharedObjects

def keepAlive():
    while True:
        stackless.schedule()

def spawnProcess(p):
    p.start()

if __name__ == '__main__':
    mgr, sharedDict, sharedList = getSharedObjects()
    mainLock = getLock()
    responseChannel = stackless.channel()
    storage = dict()
    initialTime = date(3564, 3, 5)
    tickTime = 100000
    timeChannel = stackless.channel()
    #timeChannel = sharedDict
    #timeChannel['date'] = initialTime
    p = StacklessProcess(target=generateSol, lock=mainLock, args=(8, timeChannel, responseChannel, storage, initialTime),
                         listenChannel=timeChannel, responseChannel=responseChannel)
    stackless.tasklet(spawnProcess)(p)
    #stackless.tasklet(generateSol)(8, timeChannel, responseChannel, storage, initialTime)
    stackless.tasklet(stacklessTicker)(timeChannel, tickTime, initialTime)
    s = CommunicationServer(8000, responseChannel)
    s.run()
    stackless.tasklet(keepAlive)()
    stackless.run()
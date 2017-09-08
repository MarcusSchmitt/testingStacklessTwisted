import stackless
from math import sin, cos, pi
from random import random, randint
from multiprocessing import Process, Queue, Manager

mainTasklet = None
class SolarSystem(object):
    def __init__(self, numOfPlanets, outsideChannel, storageDict):
        self.planets = list()
        self.mass = 1.75 * random() + 0.75
        self.returnChannel = outsideChannel
        self.channel = stackless.channel()
        self.storageDict = storageDict
        for i in range(numOfPlanets):
            self.planets.append(Planet(self.mass, self.storageDict, self.channel))
        stackless.tasklet(self.listenToChannel)()
    
    def listenToChannel(self):
        while True:
            makeUpdate = self.returnChannel.receive()
            if makeUpdate:
                self.channel.send(1)
                self.returnChannel.send(self.storageDict)


class Planet(object):
    def __init__(self, massOfSun, storageDict, channel):
        self.distanceToSun = 5 * random() + 0.1
        self.omega = 0.017125*(massOfSun/self.distanceToSun**3)**0.5
        self.phi = randint(0, 500) * self.omega
        self.channel = channel
        self.storageDict = storageDict
        self.storageDict[self] = (self.distanceToSun * cos(self.phi), self.distanceToSun * sin(self.phi))
        stackless.tasklet(self.waitForChannel)()
    
    def waitForChannel(self):
        while True:
            addDays = self.channel.receive()
            self.phi += self.omega * addDays
            if self.phi > 2 * pi:
                self.phi -= 2 * pi
            self.storageDict[self] = (self.distanceToSun * cos(self.phi), self.distanceToSun * sin(self.phi))


def listenToQue(que, channel):
    while True:
        message = que.get()
        if message == "UPDATE":
            channel.send(True)
            que.put("DONE")
        elif message == "KILL":
            mainTasklet.kill()


def run(que, sharedDict):
    chan = stackless.channel()
    global mainTasklet
    mainTasklet = stackless.getcurrent()
    solSyst = SolarSystem(randint(3, 12), chan, sharedDict)
    stackless.tasklet(listenToQue)(que, chan)
    stackless.run()


def makeProcess(mainQue, tickerChannel, threadChannel, sharedDict):
    solSyst = Process(target=run, args=(mainQue, sharedDict))
    solSyst.start()
    while True:
        tickerChannel.receive()
        mainQue.put("UPDATE")
        threadChannel.send(mainQue.get())
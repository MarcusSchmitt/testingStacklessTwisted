import stackless
from datetime import date, timedelta, datetime
from random import random, randint
from math import pi, cos, sin


class SolarSystem(object):
    def __init__(self, numOfPlanets, timeChannel, responseChannel, storageDict, initialTime):
        self.planets = list()
        self.mass = 1.75 * random() + 0.75
        self.timeChannel = timeChannel
        self.responseChannel = responseChannel
        self.channel = stackless.channel()
        self.storageDict = storageDict
        self.lastUpdate = initialTime
        self.numOfPlanets = numOfPlanets
        for i in range(numOfPlanets):
            self.planets.append(Planet(self.mass, self.storageDict, self.channel))
        stackless.tasklet(self.listenToChannel)()

    def listenToChannel(self):
        #lastDate = self.timeChannel['date']
        while True:
            newDate = self.timeChannel.receive()
            #newDate = self.storageDict['date']
            #while self.timeChannel['date'] <= lastDate:
                #stackless.schedule()
            #newDate = self.timeChannel['date']
            print("Tick received: ", str(datetime.now()))
            daysPassed = (newDate - self.lastUpdate).days
            daysPassed = 1 if daysPassed < 0 or daysPassed > 3e6 else daysPassed
            if daysPassed > 0:
                self.channel.send_sequence([daysPassed] * self.numOfPlanets)
                stackless.tasklet(self.sendResponse)()
                #stackless.schedule()

    def sendResponse(self):
        print("Update sent: ", str(datetime.now()))
        self.responseChannel.update(self.storageDict)

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
            daysPassed = self.channel.receive()
            self.phi += self.omega * daysPassed
            if self.phi > 2 * pi:
                self.phi -= 2 * pi
            self.storageDict[self] = (self.distanceToSun * cos(self.phi), self.distanceToSun * sin(self.phi))
            print(self, "Received Update Request: ", daysPassed, " days")


def generateSol(planets, timeChannel, responseChannel, storage, initialTime):
    solSyst = SolarSystem(planets, timeChannel, responseChannel, storage, initialTime)


def stacklessTicker(channel, tickTime, startDate):
    initTime = datetime.now()
    oldDate = startDate
    daysAdd = timedelta(days=1)
    tickTime = timedelta(microseconds=tickTime)
    nextTime = initTime  + timedelta(seconds=1)
    lastTime = nextTime + timedelta(seconds=8)
    while True:
        while datetime.now() < nextTime:
            stackless.schedule()
        nextTime += tickTime
        oldDate += daysAdd
        if nextTime > lastTime:
            sys.exit()
        value = str(datetime.now()-initTime)
        print(value)
        #channel['date'] = oldDate 
        channel.send(oldDate)

if __name__ == '__main__':
    tickerChannel = stackless.channel()
    responseChannel = stackless.channel()
    status = dict()
    stackless.tasklet(generateSol)(15, tickerChannel, responseChannel, status, date(2535, 4, 1))
    stackless.tasklet(stacklessTicker)(tickerChannel, 100000, date(2535, 4, 1))
    stackless.run()
import stackless
from datetime import date, timedelta, datetime
from random import random, randint
from math import pi, cos, sin


class SolarSystem(object):
    def __init__(self, numOfPlanets, storageDict, initialTime, timeChannel, responseChannel):
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
        print(self.timeChannel)
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
        self.responseChannel.send(self.storageDict)

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


def generateSol(planets, storage, initialTime, timeChannel, responseChannel):
    print("Generate Sol")
    print(stackless.threads)
    solSyst = SolarSystem(planets, storage, initialTime, timeChannel, responseChannel)

if __name__ == '__main__':
    tickerChannel = stackless.channel()
    responseChannel = stackless.channel()
    status = dict()
    stackless.tasklet(generateSol)(15, status, date(2535, 4, 1), tickerChannel, responseChannel)
    stackless.tasklet(stacklessTicker)(tickerChannel, 100000, date(2535, 4, 1))
    stackless.run()
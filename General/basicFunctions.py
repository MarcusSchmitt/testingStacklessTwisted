import stackless
from datetime  import date, timedelta, datetime

def stacklessTicker(channel, tickTime, startDate):
    print("Start Ticker")
    initTime = datetime.now()
    oldDate = startDate
    daysAdd = timedelta(days=1)
    tickTime = timedelta(microseconds=tickTime)
    nextTime = initTime  + timedelta(seconds=2)
    lastTime = nextTime + timedelta(seconds=8)
    while True:
        #print("Init Ticker Loop")
        while datetime.now() < nextTime:
            stackless.schedule()
        nextTime += tickTime
        #print("First Accept Loop")
        oldDate += daysAdd
        if nextTime > lastTime:
            sys.exit()
        value = str(datetime.now()-initTime)
        #print(value)
        #channel['date'] = oldDate 
        channel.send(oldDate)

def keepAlive():
    while True:
        stackless.schedule()
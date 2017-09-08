import stackless
import time
from threading import Thread
from multiprocessing import Process

def first():
    print("Function First")
    while True:
        time.sleep(1)
        stackless.schedule()

def second():
    print("Function Second")
    while True:
        time.sleep(1)
        stackless.tasklet(first)
        stackless.schedule()

def run():
    stackless.tasklet(first)()
    stackless.tasklet(second)()
    #import pdb; pdb.set_trace()
    print(stackless.getruncount() ,stackless.getthreads())
    stackless.run()

def runThread():
    t = Thread(target=run, args=())
    t.start()
    t.join()

def makeMulti():
    p = Process(target=runThread, args=())
    p.start()
    #p.join()

if __name__ == '__main__':
    stackless.tasklet(first)()
    stackless.tasklet(second)()
    stackless.run()
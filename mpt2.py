import stackless
import time
from threading import Thread, Lock
from multiprocessing import Process

def first():
    print("Function First")
    while True:
        stackless.schedule()

def second():
    print("Function Second")
    while True:
        time.sleep(1)
        #stackless.tasklet(first)()
        stackless.schedule()
        print(stackless.getruncount())

def first2():
    print("Function First2")
    while True:
        stackless.schedule()

def second2():
    print("Function Second2")
    while True:
        time.sleep(1)
        #stackless.tasklet(first)()
        stackless.schedule()
        print(stackless.getruncount())

def run():
    stackless.tasklet(first)()
    stackless.tasklet(second)()
    #import pdb; pdb.set_trace()
    print(stackless.getruncount(), stackless.getthreads())
    stackless.run()

def run2():
    stackless.tasklet(first2)()
    stackless.tasklet(second2)()
    #import pdb; pdb.set_trace()
    print(stackless.getruncount(), stackless.getthreads())
    stackless.run()

def checkedRun(func, args=None, kwargs=None):
    if stackless.getruncount() == 1:
        func()
    else:
        time.sleep(999)

def runThread(func):
    #lock.acquire()
    print(stackless.getruncount(), stackless.getthreads())
    numCurrentThreads = stackless.getthreads()
    latestThread = numCurrentThreads[-1]
    numCurrentThreads = len(numCurrentThreads)
    subthreads = list()
    for i in range(numCurrentThreads):
        subthreads.append(Thread(target=checkedRun, args=(func,)))
        subthreads[-1].start()
    print(stackless.getruncount(), stackless.getthreads())
    print(stackless.main)
    time.sleep(2)
    #lock.release()


def makeMulti(lock):
    lock.acquire()
    p = Process(target=runThread, args=(run,))
    p.start()
    time.sleep(5)
    lock.release()
    #p.join()
def makeMulti2(lock):
    #lock.acquire()
    p = Process(target=runThread, args=(run2,))
    p.start()
    time.sleep(5)
    #lock.release()
    #p.join()

if __name__ == '__main__':
    stackless.tasklet(first)()
    stackless.tasklet(second)()
    stackless.run()
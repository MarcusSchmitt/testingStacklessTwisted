import stackless
from multiprocessing import Process, Manager
from threading import Thread, Lock


def getSharedObjects():
    mgr = Manager()
    return mgr, mgr.dict(), mgr.list()


def getLock():
    return Lock()


class StacklessProcess(object):
    def __init__(self, target, args=(), kwargs={}, lock, )

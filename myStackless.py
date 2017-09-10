import stackless
allTasklets = dict()
mainTasklet = stackless.getmain()

class tasklet(stackless.tasklet):
    def __init__(self, callable):
        super().__init__(callable)
        self.name = hash(str(self))
        allTasklets[self.name] = self
    
    def killComplete(self, force = False):
        if (self == mainTasklet or self == stackless.getcurrent()) and not force:
            return 0
        super().kill()
        super().remove()
        del allTasklets[self.name]

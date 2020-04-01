from pyteleor import Mind
from pystarworlds.Agent import Body

class MyMind(Mind):

    def __init__(self):
        super(MyMind, self).__init__()
        #print("INIT MY MIND")
        self.belief1 = True
        self.belief2 = True

    def c1(self, *arg):
        #print("CALL c1:", arg)
        return True
    
    def c2(self, *arg):
        #print("CALL c2:", arg)
        return True
    

mind = MyMind()
mind.belief = "test"
body = Body(mind)

mind.decide()


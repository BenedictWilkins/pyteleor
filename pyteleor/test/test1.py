from pyteleor import Mind

class MyMind(Mind):

    def __init__(self):
        self.belief = 'The world is flat'

    def a(self, arg):
        print("CALL a:", arg)
    
MyMind()
    
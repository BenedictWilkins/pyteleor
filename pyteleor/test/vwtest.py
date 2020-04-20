import vacuumworld

from vacuumworld.vwc import action, direction, orientation

from pyteleor import Mind

class MyMind(Mind):

    __actions__ = {'move':action.move, 'turn':action.turn, 'idle':action.idle, 'clean':action.clean, 'speak':action.speak}
    __actuators__ = [] #these are defined by the vacuum world proxy mind

    def __init__(self):
        super(MyMind, self).__init__()
        self.actions = None #temporary work around
        self.grid_size = None

        #work around until i think of a better TR solution
        self.east = orientation.east
        self.west = orientation.west
        self.south = orientation.south
        self.north = orientation.north

        self.left = direction.left
        self.right = direction.right

    def decide(self):
        super(MyMind, self).decide()
        print("ACTIONS: ", self.actions)
        return self.actions

    def revise(self, observation, messages):
        self.observation = observation
        self.orientation = observation.center.agent.orientation
        self.position = observation.center.coordinate
        self.x = self.position.x #until we have dot notation in the TR program
        self.y = self.position.y

        if self.grid_size is None:
            if self.orientation == orientation.south:
                if not self.observation.forward:
                    self.grid_size = self.position.y + 1
                if not self.observation.left:
                    self.grid_size = self.position.x + 1

            if self.orientation == orientation.east:
                if not self.observation.forward:
                    self.grid_size = self.position.x + 1
                if not self.observation.right:
                    self.grid_size = self.position.y + 1
                    
            if self.orientation == orientation.west:
                if not self.observation.left:
                    self.grid_size = self.position.y + 1
                     
            if self.orientation == orientation.north:
                if not self.observation.right:
                    self.grid_size = self.position.x + 1

    def execute(self, **actions):
        #temporary work around until I update vwmind
        actions = tuple([a for a in actions.values()]) 
        if len(actions) == 0:
            self.actions = None
        elif len(actions) == 1:
            self.actions = actions[0]
        else:
            self.actions = actions

vacuumworld.run(MyMind(), skip=True, load='test.vw', play=True)
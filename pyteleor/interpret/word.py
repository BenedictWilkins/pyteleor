
class Stub:

    def eval(self, _):
        print("EVAL STUB")
        return True

    def __str__(self):
        return "STUB"
    
    def __repr__(self):
        return str(self)

class Goal:

    def __init__(self, head):
        self.__name = head
        self.__args = None #body # TODO these arguments will be ground in the call to eval by a GoalReference
        self.rules = []

    def eval(self, mind, *args): #TODO support goal arguments
        for rule in self.rules:
            if rule.eval(mind):
                return

    def __str__(self):
        return  "{0}{1}\n    {2}".format(self.__name, self.__args, "\n    ".join([str(r) for r in self.rules]))

    def __repr__(self):
        return str(self)

class Rule:

    def __init__(self, conditions, actions):
        self.__conditions = conditions
        self.__actions = actions

    def eval(self, mind):
        if all([c.eval(mind) for c in self.__conditions]):
            #print([a for a in self.__actions])
            _ = [a.eval(mind) for a in self.__actions]
            return True
        return False

    def __str__(self):
        return '{0} -> {1}'.format(self.__conditions, self.__actions)

    def __repr__(self):
        return str(self)

class Actuator:

    def __init__(self, actuator, body):
        self.__actuator = actuator
        self.__args = body

    def eval(self, mind):
        for arg in self.__args:
            #print("ATTEMPT! ") #TODO perhaps this should be given to somewhere else rather than directly to the body
            mind.execute(**{self.__actuator:arg.eval(mind)})
        return True

    def __str__(self):
        return "{0}{1}".format(self.__actuator, self.__args)

    def __repr__(self):
        return "." + str(self)

class Action:

    def __init__(self, cls, action, body):
        self.__action_cls = cls.__actions__[action] #actuators classes
        self.__args = body

    def eval(self, mind):
        return self.__action_cls(*[a.eval(mind) for a in self.__args])

    def __str__(self):
        return "{0}{1}".format(self.__action_cls.__name__, self.__args)

    def __repr__(self):
        return "." + str(self)

class Compare:

    def __init__(self, operator, arg1, arg2 ):
        self.__operator = operator
        self.__method = interpret.comparison_operators[operator]
        self.__args = (arg1, arg2) #there are 2

    def eval(self, mind):
        #print(self.__method(*[a.eval(mind) for a in self.__args]), [a.eval(mind) for a in self.__args])
        return self.__method(*[a.eval(mind) for a in self.__args])

    def __str__(self):
        return "{0} {1} {2}".format(self.__args[0], self.__operator, self.__args[1])

    def __repr__(self):
        return str(self)



class Method:

    def __init__(self, attr, *args):
        # TODO arethmetic statements?
        self.__method = attr
        self.__args = args

    def eval(self, parent):
        return self.__method(parent, *[a.eval(parent) for a in self.__args])

    def __str__(self):
        return "{0}{1}".format(self.__method.__name__, self.__args)

    def __repr__(self):
        return "." + str(self)

class Attribute:

    def __init__(self, attr):
        self.attr = attr

    def eval(self, parent):
        return getattr(parent, self.attr)

    def __str__(self):
        return self.attr

    def __repr__(self):
        return str(self)

class Literal:

    def __init__(self, value):
        self.value = value

    def eval(self, _):
        return self.value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return "." + str(self)

def is_literal(arg):
    return isinstance(arg, (int, float, bool)) or arg[0] == '\''

def is_attr(arg):
    return isinstance(arg, str) and arg[0] != '\''
from . import interpret
from . import traversal


class Program:

    def __init__(self, cls, traverse):
        
        self.__cls = cls
        self.__traversal = traverse
        def funk(fun):
            return lambda *args: fun(self, *args)
        funs = {k:funk(fun) for k,fun in Program.__dict__.items()}
        self.goals = self.__traversal.traverse(**funs)
        for g in self.goals.values():
            print(g)

        #self.traverse(cls.__pytr__)
        
    def __call__(self, mind):
        pass

        #self.goals['main'].eval(mind)

    # ===== construct program ===== #

    def goal(self, head, body, rules):
        print(" -- goal        : ", head, ":", body)
        return Goal(head, body, rules)

    def rule(self, conditions, actions):
        print(" -> rule        : ")
        print("                : ", conditions)
        print("                : ", actions)
        return Rule(conditions, actions)

    def comparison(self, head, body):
        print(" --- comparison: ", head, ":", body)
        return head, body

    def condition(self, head, body):
        print(" --- condition  : ", head, ":", body)
        return Statement(self.__cls, head, body)

    def actuator(self, head, body):
        print(" --- actuator   : ", head, ":", body)
        return Actuator(head, body)
    
    def goal_action(self, head, body):
        print(" --- goalaction : ", head, ":", body)
        return head, body

    def action(self, head, body):
        print(" ---- action    : ", head, ":", body)
        return Action(self.__cls, head, body)

    def statement(self, head, body):
        #print(" ----- statement: ", head, ":", body)
        return Statement(self.__cls, head, body)

    def literal(self, value):
        #print(" ----- literal  : ", value)
        return Literal(value)

    def attribute(self, attr):
        #print(" ----- attribute: ", attr)
        return Attribute(attr)

class Stub:

    def eval(self, mind):
        return True

    def __str__(self):
        return "TODO"
    
    def __repr__(self):
        return str(self)

class Goal:

    def __init__(self, head, body, rules):
        self.__name = head
        self.__args = body
        self.__rules = rules

    def eval(self, mind):
        for rule in self.__rules:
            rule.eval(mind)

    def __str__(self):
        return  "{0}{1}\n    {2}".format(self.__name, self.__args, "\n    ".join([str(r) for r in self.__rules]))

    def __repr__(self):
        return str(self)

class Rule:

    def __init__(self, conditions, actions):
        self.__conditions = conditions
        self.__actions = actions

    def eval(self, mind):
        if all([c.eval(mind) for c in self.__conditions]):
            #goal checking, did the goal fail? if so we should continue executing rules, otherwise we start over
            return all([a.eval(mind) for a in self.__actions]) 
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
            mind.body.attempt(**{self.__actuator:arg.eval(mind)})

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

class Statement:

    def __init__(self, cls, head, body):
        # TODO arethmetic statements?
        self.__method = getattr(cls, head)
        self.__args = body

    def eval(self, mind):
        return self.__method(mind, *[a.eval(mind) for a in self.__args])

    def __str__(self):
        return "{0}{1}".format(self.__method.__name__, self.__args)

    def __repr__(self):
        return "." + str(self)

class Attribute:

    def __init__(self, attr):
        self.attr = attr

    def eval(self, mind):
        return getattr(mind, self.attr)

    def __str__(self):
        return self.attr

    def __repr__(self):
        return "." + str(self)

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
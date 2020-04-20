from . import interpret
from . import traversal


class Program:

    def __init__(self, cls, traverse):
        
        self.__cls = cls
        self.__traversal = traverse
        self.__goal_references = []

        def funk(fun):
            return lambda *args: fun(self, *args)
        funs = {k:funk(fun) for k,fun in Program.__dict__.items()}

        self.goals = {k:Goal(k) for k in self.__traversal.goals}

        self.__traversal.traverse(**funs)

    
    def __str__(self):
        return "\n".join([str(g) for g in self.goals.values()])

    def __repr__(self):
        return str(self)

    def __call__(self, mind):
        self.goals['main'].eval(mind)

    # ===== construct program ===== #

    def goal(self, head, body, rules):
        #print(" -- goal        : ", head, ":", body)
        goal = self.goals[head]
        goal.rules = rules
        return goal

    def rule(self, conditions, actions):
        #print(" -> rule        : ")
        #print("                : ", conditions)
        #print("                : ", actions)
        return Rule(conditions, actions)

    def comparison(self, head, body):
        #is this every going to happen? it probably shouldnt...
        if isinstance(body[0], Literal) and isinstance(body[1], Literal):
            #the expression can be evaluated immediately, do it now!
            value = interpret.comparison_operators[head](body[0].value, body[1].value)
            #TODO if this is false something is wrong, otherwise we should not turn anything?
            return Literal(value)
        #print(" --- comparison: ", head, ":", body)
        return Compare(head, body)

    def condition(self, head, body):
        #print(" --- condition  : ", head, ":", body)
        return Statement(self.__cls, head, body)

    def actuator(self, head, body):
        #print(" --- actuator   : ", head, ":", body)
        return Actuator(head, body)
    
    def goal_action(self, head, body):
        #print(" --- goalaction : ", head, ":", body)
        return GoalReference(head, body, self.goals[head])
       
    def action(self, head, body):
        #print(" ---- action    : ", head, ":", body)
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

    def eval(self, _):
        print("EVAL STUB")
        return True

    def __str__(self):
        return "STUB"
    
    def __repr__(self):
        return str(self)

class GoalReference: #TODO this can be made a Statement?

    def __init__(self, head, body, goal):
        self.__name = head
        self.__args = body
        self.__goal = goal

    def eval(self, mind):
        return self.__goal.eval(mind, *[a.eval(mind) for a in self.__args])

    def __str__(self):
        return "{0}{1}".format(self.__method.__name__, self.__args)

class Goal:

    def __init__(self, head):
        self.__name = head
        self.__args = None #body # TODO these arguments will be ground in the call to eval by a GoalReference
        self.rules = None

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

    def __init__(self, head, body):
        self.__operator = head
        self.__method = interpret.comparison_operators[head]
        self.__args = body #there are 2

    def eval(self, mind):
        #print(self.__method(*[a.eval(mind) for a in self.__args]), [a.eval(mind) for a in self.__args])
        return self.__method(*[a.eval(mind) for a in self.__args])

    def __str__(self):
        return "{0} {1} {2}".format(self.__args[0], self.__operator, self.__args[1])

    def __repr__(self):
        return str(self)

class Statement:

    def __init__(self, cls, head, body):
        # TODO arethmetic statements?
        self.__method = getattr(cls, head)
        self.__args = body

    def eval(self, mind):
        #print(" -- ", self.__method.__name__, *[a.eval(mind) for a in self.__args])
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
        return str(self)

class Literal:

    def __init__(self, value):
        self.value = value

    def eval(self, _):
        return self.value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)





def is_literal(arg):
    return isinstance(arg, (int, float, bool)) or arg[0] == '\''

def is_attr(arg):
    return isinstance(arg, str) and arg[0] != '\''
from pprint import pprint
from collections import defaultdict
try:
    from . import interpret
except:
    pass

class LinkException(Exception): #TODO move this to a common place..
    MESSAGE = "Failed to link with TR program, "

class Meta:

    def __init__(self):
        super(Meta, self).__init__()
        self.actions = set()
        self.actuators = defaultdict(set)
        self.methods = set()
        self.attributes = set()

    def condition(self, head, body):
        self.methods.add(head)
        return head, body

    def actuator(self, head, body):
        for arg in body:
            self.actuators[head].add(arg[0])
        return head, body
    
    def action(self, head, body):
        self.actions.add(head)
        return head, body

    def statement(self, head, body):
        self.methods.add(head)
        return head, body
    
    def attribute(self, attr):
        self.attributes.add(attr)
        return attr

class Traverse:
    
    def __init__(self, program):
        super(Traverse, self).__init__()
        self.program = program

        self.funs = defaultdict(lambda : lambda *args: args)

        self.__goals = set() #required for initial traversal
        for goal in program: 
            goal = goal[0][2][0]
            if goal in self.goals:
                raise LinkException("Goal {0} has been defined more than once.".format(goal))
            self.__goals.add(goal)

        self.__meta = Meta()
        def funk(fun):
            return lambda *args: fun(self.__meta, *args)
        meta_funs = {k:funk(fun) for k,fun in Meta.__dict__.items()}
        self.__t_traverse(**meta_funs)

        pprint(self.goals)
        pprint(self.actuators)
        pprint(self.actions)
        pprint(self.methods)
        pprint(self.attributes)

    def __t_traverse(self, **funs):
        self.funs.update(**funs)
        goals = {}

        for goal in self.program:
            g = self.__t_goal(goal[0], goal[1:])
            goals[goal[0][2][0]] = g

        self.funs.clear()

        return goals
    
    def traverse(self, **funs):
        return self.__t_traverse(**funs)

    @property
    def goals(self):
        return self.__goals
    @property
    def actuators(self):
        return self.__meta.actuators
    @property
    def actions(self):
        return self.__meta.actions
    @property
    def methods(self):
        return self.__meta.methods
    @property
    def attributes(self):
        return self.__meta.attributes

    def __t_goal(self, head, body):
        rules = [self.__t_rule(rule[2][0], rule[2][1]) for rule in body]
        return self.funs['goal'](head[2][0], head[2][1], rules)

    def __t_rule(self, conditions, actions):
        
        p_conditions = [self.__t_condition(condition[0], *condition[1:]) for condition in conditions]
            
        p_actions = []
        for action in actions:
            if action[0] in self.goals:
                #TODO more meaningful error message/refactor
                if len(actions) > 1:
                    raise LinkException("goal-action rules are not supported TODO...")
                p_actions.append(self.__t_goal_action(action[0], action[1]))
            else:
                p_actions.append(self.__t_actuator(action[0], action[1]))
        
        return self.funs['rule'](p_conditions, p_actions)

    def __t_condition(self, head, *body):
        if head in interpret.comparison_operators:
            args = [self.__t_arg(arg) for arg in body[0]]
            return self.funs['comparison'](head, args) #TODO
        else:
            if len(body) == 0:
                return self.funs['attribute'](head)
            else:
                args = [self.__t_arg(arg) for arg in body[0]]
                return self.funs['condition'](head, args)

    def __t_goal_action(self, head, body):
        args = [self.__t_arg(arg) for arg in body]
        return self.funs['goal_action'](head, args)

    def __t_actuator(self, head, body):
        actions = []
        for action in body:
            if len(action) == 1:
                #this makes things easier down the line
                #allows for syntax actuator1(a1) rather than actuator1(a1())
                actions.append(self.__t_action(action[0], ()))
            elif len(action) == 2:
                actions.append(self.__t_action(action[0], action[1]))
            else:
                assert False # what happend?!
            
        return self.funs['actuator'](head, actions)

    def __t_action(self, head, body):
        args = [self.__t_arg(arg) for arg in body]
        return self.funs['action'](head, args)

    def __t_arg(self, arg):
        if isinstance(arg, tuple):
            if len(arg) == 1:
                return self.__t_attribute(arg[0])
            elif len(arg) == 2:
                return self.__t_statement(arg[0], arg[1])
            else: 
                assert False # what happend?!
        else:
            return self.__t_literal(arg)

    def __t_statement(self, head, body):
        args = [self.__t_arg(arg) for arg in body]
        return self.funs['statement'](head, args)

    def __t_literal(self, value):
        return self.funs['literal'](value)
    
    def __t_attribute(self, attr):
        return self.funs['attribute'](attr)

class TraverseTest(Traverse):

    def __init__(self, program):
        super(TraverseTest, self).__init__(program)

    def __call__(self):
        def funk(fun):
            return lambda *args: fun(self, *args)
        funs = {k:funk(fun) for k,fun in TraverseTest.__dict__.items()}
        super(TraverseTest, self).traverse(**funs)

    def goal(self, head, body, rules):
        print(" -- goal        : ", head, ":", body)
        return head, body

    def rule(self, conditions, actions):
        print(" -> rule        : ")
        print("                : ", conditions)
        print("                : ", actions)
        return conditions, actions

    def comparison(self, head, body):
        print(" --- comparison: ", head, ":", body)
        return head, body

    def condition(self, head, body):
        print(" --- condition  : ", head, ":", body)
        return head, body

    def actuator(self, head, body):
        print(" --- actuator   : ", head, ":", body)
        return head, body
    
    def goal_action(self, head, body):
        print(" --- goalaction : ", head, ":", body)
        return head, body

    def action(self, head, body):
        print(" ---- action    : ", head, ":", body)
        return head, body

    def statement(self, head, body):
        print(" ----- statement: ", head, ":", body)
        return head, body

    def literal(self, value):
        print(" ----- literal  : ", value)
        return value

    def attribute(self, attr):
        print(" ----- attribute: ", attr)
        return attr

if __name__ == "__main__":
    
    from pyteleor import interpret

    with open('/home/ben/repos/pyteleor/pyteleor/test/MyMind.pytr') as f:
        program = interpret.parse(f.read())
        t = TraverseTest(program)
        t()
    
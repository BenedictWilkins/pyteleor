
from . import interpret
from . import program
from . import traversal

import sys, os
from pprint import pprint
from collections import defaultdict, UserDict
from types import SimpleNamespace

from pystarworlds.Event import new_action
from pystarworlds.Agent import Mind as BaseMind, InternalAgentError, BodyComponent, Body as BaseBody, new_actuator

PYTR_EXTENSION = ".pytr"

__all__ = ('traverse', 'program', 'interpret')

class LinkException(Exception):
    MESSAGE = "Failed to link with TR program, "

    def __init__(self, message, *args, **kwargs):
        super(LinkException, self).__init__(LinkException.MESSAGE + message, *args, **kwargs)

def _hasattr(obj, attr):
    if not hasattr(obj, attr):
        raise LinkException("\'{0}\' is not an attribute of object of type: \'{1}\'".format(attr, obj.__class__.__name__))

class ClassRecordDict(UserDict):

    def __init__(self, cls_factory):
        super(ClassRecordDict, self).__init__()
        self.cls_factory = cls_factory

    def __getitem__(self, key):
        if key not in self:
            self[key] = self.cls_factory(key)
        return super().__getitem__(key)

def load_program(c):
    path = os.path.abspath(sys.modules[c.__module__].__file__)
    path = os.path.dirname(path)
    path = os.path.join(path, c.__name__ + PYTR_EXTENSION)
    if os.path.exists(path): #TODO there is not support for inheritance... maybe we dont want this ...
        with open(path) as f:
            try:
                return interpret.parse(f.read())
            except:
                #there was an error
                raise ValueError("parse error... TODO")
    return [] #empty program


class MetaMind(type):

    def __call__(cls, *args, **kwargs):
        mind = type.__call__(cls, *args, **kwargs)
        if not hasattr(mind, '_BodyComponent__body'): #TODO is there a way to ensure that init on super is always called?
            raise InternalAgentError("Class {0} must call super __init__".format(cls.__name__))
        
        return mind

    def __new__(cls, name, bases, dct):
        c = super().__new__(cls, name, bases, dct) #create a temporary class to get src file details
        
        __pytr__ = load_program(c)
        if len(__pytr__) == 0:
            return c

        dct['__pytr__'] =  __pytr__ #create a place to store the parsed code
        pp = traversal.Traverse(__pytr__)

         # TODO move all this into __pytr__ to prevent cluttering the class properties?
        #create classes for each actions
        action_cls = {}
        for action in pp.actions:
                action_cls[action] = new_action(action)
        dct['__actions__'] =  action_cls #action classes

        #create a class for each actuator
        actuator_cls = {}
        for actuator, actions in pp.actuators.items():
            actuator_cls[actuator] = new_actuator(actuator, *actions)
        dct['__actuators__'] = actuator_cls #actuators classes

        dct['__goals__'] = pp.goals
        dct['__program__'] = None #build it

        #create a property for every attribute
        for attr in pp.attributes:
            if attr in dct:
                raise LinkException("Attribute {0} has already been defined as a class property".format(attr))

            instance_attr = '_{0}__{1}'.format(name, attr)
            def attr_getter(self):
                return getattr(self, instance_attr)

            def attr_setter(self, value):
                print("SET BELIEF: ", instance_attr)
                # TODO update a flag, any condition containing this attr needs to be re-evaluated
                #self.__program__.changed(attr)
                setattr(self, instance_attr, value)
            dct[attr] = property(attr_getter, attr_setter)

        #check that all of the required methods are present in the class
        for method in pp.methods:
            if not method in dct:
                raise LinkException("Method '{0}' is defined in TR program but not in class '{1}'".format(method, name))
            if not callable(dct[method]):
                raise LinkException("Method '{0}' is defined in TR program but is not callable in class '{1}'".format(method, name))
        
        #create the program
        
        # create class
        c = super().__new__(cls, name, bases, dct)
        c.__program__ = program.Program(c, pp)
        
        return c


class Mind(BaseMind, metaclass=MetaMind):

    def __init__(self, *args, **kwargs):
        super(Mind, self).__init__(*args, **kwargs)

    def cycle(self):
        #observation = self.body.sensors['sensor']() #pull percepts from each sensor
        perceptions = perceive()
        revise(**perceptions)

        actions = decide()
        execute(**actions)

    @BodyComponent.body.setter
    def body(self, value: BaseBody):
        self._BodyComponent__body = value
        if value is not None: #add new actuators to body
            if len(self.body.actuators) != 0:
                raise InternalAgentError("Failed to create TR actuators for agent {0}: actuators already exist".format(str(value)))
            for actuator_name, actuator_cls in self.__class__.__actuators__.items():
                actuator = actuator_cls()
                self.body.add_actuator(actuator)
        
    def perceive(self):
        '''
            Pull perceptions from sensors, perceptions will be given the revise.
        '''
        pass #TODO

    def revise(self, **perceptions):
        '''
            Each observation in perceptions may contain some data from the given sensor, i.e.
            perceptions = {sensor1:sensor1_data, sensor2:sensor2_data, ...}. This method should 
            update the agents knowledge base, it is always called before decide.
        '''
        pass # TODO

    def decide(self):
        '''
            Runs the TR program associated with this agent, retrieves any actions.
        '''
        self.__class__.__program__(self)














'''

class Linker:

    def __init__(self, mind):
        self.pytr = mind.__class__.__pytr__ #program

        if self.pytr is None:
            raise ValueError("??")

        self.mind = mind

    def __call__(self):
        goals = [self.resolve_goal(goal[0], goal[1:]) for goal in self.pytr]

    def resolve_goal(self, head, body):
        print("goal", head)
        return [r for r in self.resolve_rules(body)]
    
    def resolve_rules(self, goal):
        for rule in goal:
            conditions = rule[2][0]
            r = program.Rule()
            for condition in conditions:
                r.add_condition(self.mind, condition[0], condition[1])
        

            yield r


    def resolve_conditions(self, conditions):
        for condition in conditions:
            yield self.resolve_condition(condition[0], condition[1])

    def resolve_actions(self, actions):
        for action in actions:
            yield self.resolve_action(action)
    
    def resolve_action(self, action):
        print("---- action", action)
        #create actuator for action if it doesnt exist?
        actuator_name = action[0]

        action_name = action[1][0]
        action_args = [self.resolve_statement(arg) for arg in action[1][1]]
        a_cls = self.actions[action_name]

        self.actuator_spec[actuator_name].add(action_name) #TODO change
        
        action_meta = "{0}/{1}".format(action_name, len(action_args))

        return (actuator_name, (action_meta, (a_cls, action_args)))


    def resolve_condition(self, name, args):
        print("---- condition", name, args)
        return 
        
        #args = [self.resolve_arg(arg) for arg in args]
        #meta = "{0}/{1}".format(name, len(args))


        if name in interpret.comparison_operators:
            return meta, lambda: interpret.comparison_operators[name](*[arg() for arg in args])
        else:
            _hasattr(self.mind, name)
            #TODO check number of args of the method (check signature matches)
            return meta, lambda: getattr(self.mind, name)(*[arg() for arg in args])

    def resolve_statement(self, statement):
        if isinstance(statement, tuple):
            name = statement[0]
            args = [self.resolve_statement(arg) for arg in statement[1]]
            return lambda: getattr(self.mind, name)(*[arg() for arg in args])
        else:
            return self.resolve_arg(statement)

    def resolve_arg(self, arg):
        #TODO a better check?
        if isinstance(arg, (int, float, bool)) or arg[0] == '\'' or arg[0] == '\"':
            return lambda : arg
        else:
            _hasattr(self.mind, arg) #if the argument hasnt been declared, it should have been...?
            return (arg, lambda : getattr(self.mind, arg))
'''
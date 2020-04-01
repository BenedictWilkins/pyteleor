
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
        if '__actions__' not in dct:
            #create classes for each actions if they dont exist
            action_cls = {}
            for action in pp.actions:
                    action_cls[action] = new_action(action)
            dct['__actions__'] = action_cls #action classes

        if '__actuators__' not in dct:
            #create a class for each actuator if they dont exist
            actuator_cls = {}
            for actuator, actions in pp.actuators.items():
                actuator_cls[actuator] = new_actuator(actuator, *actions)
            dct['__actuators__'] = actuator_cls #actuators classes
            
        dct['__program__'] = None #build it

        #create a property for every attribute
        instance_attrs = []

        def _property(instance_attr):
            def attr_getter(self):
                return getattr(self, instance_attr)

            def attr_setter(self, value):
                print("SET BELIEF: ", instance_attr, value)
                # TODO update a flag, any condition containing this attr needs to be re-evaluated
                #self.__program__.changed(attr)
                setattr(self, instance_attr, value)

            return property(attr_getter, attr_setter)

        for attr in pp.attributes:
            if attr in dct:
                raise LinkException("Attribute {0} has already been defined as a class property".format(attr))

            instance_attr = '_{0}__{1}'.format(name, attr)
            instance_attrs.append(instance_attr)

            dct[attr] = _property(instance_attr)

        #check that all of the required methods are present in the class
        for method in pp.methods:
            if not method in dct:
                raise LinkException("Method '{0}' is defined in TR program but not in class '{1}'".format(method, name))
            if not callable(dct[method]):
                raise LinkException("Method '{0}' is defined in TR program but is not callable in class '{1}'".format(method, name))
        
        # decorate __init__ to add all instance attributes
        def init_decorator(fun):
            def funk(self, *args, **kwargs):
                self.__dict__.update({attr:None for attr in instance_attrs})
                fun(self, *args, **kwargs)
            return funk
        
        #create class
        c = super().__new__(cls, name, bases, dct)

        c.__init__ = init_decorator(c.__init__)
        c.__program__ = program.Program(c, pp)
        
        return c

class Mind(BaseMind, metaclass=MetaMind):

    def __init__(self, *args, **kwargs):
        super(Mind, self).__init__(*args, **kwargs)

    def cycle(self):
        #observation = self.body.sensors['sensor']() #pull percepts from each sensor
        self.revise(**self.body.perceive())
        self.decide()

    @BodyComponent.body.setter
    def body(self, value: BaseBody):
        self._BodyComponent__body = value
        if value is not None: #add new actuators to body
            if len(self.body.actuators) != 0:
                raise InternalAgentError("Failed to create TR actuators for agent {0}: actuators already exist".format(str(value)))
            for actuator_name, actuator_cls in self.__class__.__actuators__.items():
                actuator = actuator_cls()
                self.body.add_actuator(actuator, name=actuator_name)
        
    def revise(self, **perceptions):
        '''
            Each observation in perceptions may contain some data from the given sensor, i.e.
            perceptions = {sensor1:sensor1_data, sensor2:sensor2_data, ...}. This method should 
            update the agents knowledge base, it is always called before decide.
        '''
        pass # TODO

    def decide(self):
        '''
            Runs the TR program associated with this agent. Any actions that are generated will be sent to execute.
        '''
        self.__class__.__program__(self)

    def execute(self, **actions):
        '''
            Attempts any actions via the appropriate actuator.
        '''
        print("EXECUTE: ", actions)
        pass




from . import interpret
import sys, os
from pprint import pprint

PYTR_EXTENSION = ".pytr"

class LinkException(Exception):
    MESSAGE = "Failed to link with TR program, "

    def __init__(self, message, *args, **kwargs):
        super(LinkException, self).__init__(LinkException.MESSAGE + message, *args, **kwargs)




def _hasattr(obj, attr):
    if not hasattr(obj, attr):
        raise LinkException("condition with name \'{0}\' is not an attribute of object of type: \'{1}\'".format(attr, obj.__class__.__name__))

def resolve_arg(obj, arg):
    if isinstance(arg, (int, float)) or arg[0] == '\'' or arg[0] == '\"':
        return lambda : arg
    else:
        _hasattr(obj, arg)
        return lambda : getattr(obj, arg)

def resolve_condition(obj, condition):
    name = condition[0]
    args = condition[1]

    args = [resolve_arg(obj, arg) for arg in args]

    if name in interpret.comparison_operators:
        return lambda: interpret.comparison_operators[name](*[arg() for arg in args])
    else:
        _hasattr(obj, name)
        #TODO check number of args of the method (check signature matches)
        return lambda: getattr(obj, name)(*[arg() for arg in args])

def link(mind):
    pytr = mind.__class__.__pytr__
    #pprint(mind.__dict__)

    for rule in pytr:
        print("rule: ", rule)
        conditions = rule[0]
        for c in conditions:
            r_c = resolve_condition(mind, c)
            r_c() #test...    
        
    return mind

class MetaMind(type):

    def __call__(cls, *args, **kwargs):
        return link(type.__call__(cls, *args, **kwargs))

    def __new__(cls, name, bases, dct):
        dct['__pytr__'] = None #create a place to store the parsed code
        #print(cls)
        #print(name)
        #print(bases)
        #print(dct)
       
        c = super().__new__(cls, name, bases, dct)

        if len(bases) > 0: #i.e. not Mind
            class_path = os.path.abspath(sys.modules[c.__module__].__file__)
            class_path = os.path.dirname(class_path)
            class_path = os.path.join(class_path, name + PYTR_EXTENSION)

            with open(class_path) as f:
                c.__pytr__ = interpret.yacc.parse(f.read())
                
        return c



class Mind(metaclass=MetaMind):

    def __init__(self, *args, **kwargs):
        super(Mind, self).__init__(*args, **kwargs)




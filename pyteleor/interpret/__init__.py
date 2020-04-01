from ply import lex
from ply import yacc

import copy

tokens = ('COMMENT', 'STR', 'NAME', 'IMPLY', 'LPAREN', 'RPAREN', 'COMMA', 'NEWLINE',
          'FLOAT', 'INT', 'LT', 'GT', 'LTE', 'GTE', 'E', 'NE', 'COLON', 'BOOL', 'NONE')

t_COMMENT = r"\#[^\n]*"
#t_STR = r"[\'\"](.+?)[\'\"]"
t_NAME = r"[a-zA-Z]+[a-zA-z0-9]*"
t_IMPLY = r"->"
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_COMMA = r","

def t_NONE(t):
    r"None"
    t.value = None
    return t

def t_BOOL(t):
    r"(True|False)"
    t.value = bool(t.value)
    return t

def t_FLOAT(t):
    r"-?[0-9]+\.[0-9]*"
    t.value = float(t.value) #all numbers are treated as floats
    return t

def t_INT(t):
    r"-?[0-9]+"
    t.value = int(t.value)
    return t

#comparison operators
t_LT  = r"<"
t_GT  = r">"
t_LTE = r"<="
t_GTE = r">="
t_E   = r"=="
t_NE  = r"!="

comparison_operators = {t_LT:lambda x, y: x < y,
                        t_GT:lambda x, y: x > y,
                        t_LTE: lambda x, y: x <= y,
                        t_GTE: lambda x, y: x >= y,
                        t_E: lambda x, y: x == y,
                        t_NE: lambda x, y: x != y}

t_ignore = " \t"

# used in post processing for indentation checks
INDENT_COUNT = [0]
GOAL_INDEX = []

def t_NEWLINE(t):
    r'\n[ ]*'
    #print('('+t.value.replace('\n','')+')', t.value.count(" "))
    INDENT_COUNT.append(t.value.count(" "))
    t.lexer.lineno += 1
    return t

def t_COLON(t):
    r':'
    GOAL_INDEX.append(t.lexer.lineno - 1)
    return t

def t_STR(t):
    r"[\'\"](.+?)[\'\"]"
    t.value = t.value.replace("\"", "\'")
    return t

lex.lex()

def p_program_n(p):
    ''' program : program NEWLINE line '''
    p[0] = [*p[1], p[3]]

def p_program_1(p):
    ''' program : line '''
    p[0] = [p[1]]

def p_line(p):
    ''' line : plan
             | plan COMMENT
             | rule
             | rule COMMENT '''
    p[0] = p[1]
    #print('line:',p[0])

def p_plan(p):
    '''plan : statement COLON '''
    p[0] = p[1]

def p_line_empty(p):
    ''' line : COMMENT
             | empty '''
    p[0] = ()
    #print('line:',p[0])

def p_rule(p):
    '''rule : conditions IMPLY actions '''
    p[0] = (p[1], p[3]) #conditions, actions
    
# conditions
def p_conditions0(p):
    ''' conditions : empty '''
    p[0] = []

def p_conditions1(p):
    ''' conditions : condition '''
    p[0] = [p[1]]

def p_conditionsn(p):
    ''' conditions : condition COMMA conditions '''
    p[0] = [p[1], *p[3]]

# actions
def p_actions0(p):
    ''' actions : empty '''
    p[0] = []

def p_actions1(p):
    ''' actions : action '''
    p[0] = [p[1]]

def p_actionsn(p):
    ''' actions : action COMMA actions '''
    p[0] = [p[1], *p[3]]

def p_action(p):
    ''' action :  NAME LPAREN args RPAREN '''
    p[0] = (p[1], p[3])

def p_condition(p):
    ''' condition : statement '''
    p[0] = p[1]

def p_condition1(p):
    ''' condition : NAME '''
    p[0] = (p[1],)

def p_statement(p):
    '''statement : NAME LPAREN args RPAREN'''
    p[0] = (p[1], p[3])
    #print('statement', p[0])

def p_compare(p):
    ''' condition : arg operator arg '''
    p[0] = (p[2], (p[1], p[3]))

def p_coperator(p):
    ''' operator : LT 
                 | GT 
                 | LTE
                 | GTE 
                 | E 
                 | NE '''
    p[0] = p[1]

def p_empty(p):
    'empty : '
    pass

def p_args0(p):
    ''' args : empty'''
    p[0] = tuple()

def p_args1(p):
    ''' args : arg '''
    p[0] = (p[1],)

def p_argsn(p):
    ''' args : arg COMMA args '''
    p[0] = (p[1], *p[3])

def p_literal(p):
    ''' arg : STR
            | FLOAT
            | INT 
            | BOOL
            | NONE
    '''
    p[0] = p[1]

def p_arg_statement(p):
    '''arg : statement '''
    p[0] = p[1]

def p_arg(p):
    '''arg : NAME ''' 
    p[0] = (p[1],)

yacc.yacc()

class ParseError(Exception):
    pass

class IdentationError(Exception):
    pass


def parse(program):

    
    def process_plan(plan): #TODO plans are now called goals
        plan_name = plan[0][3]

        plan = [j for j in plan if j[2] != ()] #remove all empty lines
        if len(plan) <= 1:
            raise ParseError("Parse Error: Empty plan: {0}".format(plan_name))

        head_indent = plan[0][1]
        body_indent = plan[1][1]
        #print(head_indent, body_indent)
        if head_indent >= body_indent:
            raise IdentationError("Indentation Error: body of plan '{0}' at line {1} - '{2}' must be indented".format(plan_name, plan[1][0], plan[1][3]))

        for l in plan[1:]:
            if l[1] != body_indent:
                raise IdentationError("Indentation Error: Inconsistent indentation {0} at line {1} - '{2}'".format(l[1], l[0], l[3]))

        return plan

 
    program = "main():\n" + program.rstrip()
    s_program = program.split('\n')
    #print(program)
    
    p = yacc.parse(program)
    
    i = INDENT_COUNT

    #TODO refactor this is quick and dirty...
    p = [(j, i[j], p[j], s_program[j].rstrip()) for j in range(len(p))] #line_number, indent, line_data, line_text
    p[0] = (p[0][0], -1, *p[0][2:]) #special case of main plan, negative indent to prevent errors

    GOAL_INDEX.append(len(p))
    p = [p[GOAL_INDEX[k]:GOAL_INDEX[k+1]] for k in range(len(GOAL_INDEX)-1)]
    
    for k in range(len(p)): #remove all empty lines
        p[k] = process_plan(p[k])

    GOAL_INDEX.clear()
    INDENT_COUNT.clear()
    INDENT_COUNT.append(0) #main is always at indent 0

    def debug(): #TODO remove
        for plan in p:
            print(plan[0])
            for l in plan[1:]:
                print("  ", l)  
    #debug()
    
    return p
    
if __name__ == "__main__": 
    import os

    print(os.path.dirname(__file__) )
    with open(os.path.dirname(__file__)  + "/../test/MyMind.pytr") as f:
        p = parse(f.read())
        #p = yacc.parse("\n" + f.read().strip())
'''
    yacc.parse("a(\"test\") -> b() \n a() -> d(1) #comment \n #comment2 \n")

    while True:
        try:
            s = input(' > ')
        except EOFError:
            break
        yacc.parse(s)
'''
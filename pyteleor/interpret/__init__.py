from ply import lex
from ply import yacc

tokens = ('NAME', 'IMPLY', 'LPAREN', 'RPAREN', 'COMMA', 
          'FLOAT', 'INT', 'LT', 'GT', 'LTE', 'GTE', 'E')

t_NAME = r"[a-zA-Z]+[a-zA-z0-9]*"
t_IMPLY = r"->"
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_COMMA = r","

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
 
t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

lex.lex()

def p_rule(p):
    '''rule : conditions IMPLY actions'''
    print('rule:')
    print('-- conditions:')
    for c in p[1]:
        print("   ", c)
    print('-- actions')
    for a in p[3]:
        print("   ", a)

# conditions
def p_conditions0(p):
    ''' conditions : empty '''
    p[0] = tuple()

def p_conditions1(p):
    ''' conditions : condition '''
    p[0] = (p[1],)

def p_conditionsn(p):
    ''' conditions : condition COMMA conditions '''
    p[0] = [p[1], *p[3]]

# actions
def p_actions0(p):
    ''' actions : empty '''
    p[0] = tuple()

def p_actions1(p):
    ''' actions : action '''
    p[0] = (p[1],)

def p_actionsn(p):
    ''' actions : action COMMA actions '''
    p[0] = [p[1], *p[3]]

def p_action(p):
    ''' action : statement '''
    p[0] = p[1]

def p_condition(p):
    ''' condition : statement '''
    p[0] = p[1]

def p_statement(p):
    '''statement : NAME LPAREN args RPAREN'''
    p[0] = [p[1], p[3]]
    print('statement', '~'.join([str(s) for s in p]))


def p_compare(p):
    ''' condition : arg operator arg '''
    p[0] = [p[2], (p[1], p[3])]

def p_coperator(p):
    ''' operator : LT 
                 | GT 
                 | LTE
                 | GTE 
                 | E '''
    p[0] = p[1]

def p_empty(p):
    'empty :'
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

def p_arg(p):
    '''arg : NAME 
           | FLOAT
           | INT ''' 
    p[0] = p[1]

yacc.yacc()

while True:
    try:
        s = input('calc > ')
    except EOFError:
        break
    yacc.parse(s)
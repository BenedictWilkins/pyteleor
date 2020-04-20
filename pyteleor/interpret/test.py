from ply import lex
from ply import yacc


tokens = ('NAME', 'IMPLY', 'DOT', 'COMMA', 'NEWLINE', 'COLON')

t_NAME = r"[a-zA-Z]+[a-zA-z0-9]*"
t_IMPLY = r"->"
t_COMMA = r","
t_DOT = r"\."

t_ignore = " \t"

def t_NEWLINE(t):
    r'\n[ ]*'
    t.lexer.lineno += 1
    return t

def t_COLON(t):
    r':'
    return t

lex.lex()

def p_program_n(p):
    ''' program : program NEWLINE line '''
    p[0] = [*p[1], p[3]]

def p_program_1(p):
    ''' program : line '''
    p[0] = [p[1]]

def p_line(p):
    ''' line : satoms COLON
             | atoms IMPLY '''
    p[0] = p[1]

def p_satoms(p):
    ''' satoms : ndot COMMA satoms '''
    p[0] = [p[1], *p[3]]

def p_satoms1(p):
    ''' satoms : ndot '''
    p[0] = p[1]

def p_atoms(p):
    ''' atoms : ndot COMMA atoms
              | NAME COMMA atoms '''
    p[0] = [p[1], *p[3]]

def p_atoms1(p):
    ''' atoms : NAME 
              | ndot '''
    p[0] = p[1]

def p_ndot(p):
    ''' ndot : NAME DOT '''
    p[0] = p[1]

yacc.yacc()


def parse(program):
    p = yacc.parse(program)
    return p
    
if __name__ == "__main__": 
    p = parse("a.,b.,c.:\n d,e,f->")  
    print(p)
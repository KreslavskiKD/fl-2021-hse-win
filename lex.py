import ply.lex as lex
import sys

reserved = {
    'def': 'def',
    'class': 'class',
    'override': 'override',
    'fun': 'fun',
    'return': 'return',
    'start': 'start',
    'else': 'else',
    'deadend': 'deadend',
    'alphabet': 'alphabet',
    'terminal': 'terminal',
    'itself': 'itself'
}

tokens = [
             'INT',
             'STRING',
             'CHAR',
             'ARROW',
             'ID',
             'CLASSNAME',
             'TYPIZATION',
             'CONSTRUCTOR',
             'BLOCKSTART',
             'BLOCKEND',
             'PARSTART',
             'PAREND',
             'EQUALITY',
             'COMMA',
             'METHOD',
             'LOGICOPERATOR',
             'COMPAREOPERATOR'
         ] + list(reserved.values())


def t_INT(t):
    r'[0-9]+'
    t.value = int(t.value)
    t.type = reserved.get(t.value, 'INT')
    return t


def t_STRING(t):
    r'\"[a-z_0-9A-Z]*\"'
    t.value = str(t.value)
    t.type = reserved.get(t.value, 'STRING')
    return t


def t_CHAR(t):
    r"\'.\'"
    t.value = str(t.value)[1]
    t.type = reserved.get(t.value, 'CHAR')
    return t


def t_ID(t):
    r'[a-z_][a-z_0-9A-Z]*'
    t.type = reserved.get(t.value, 'ID')
    return t


def t_CONSTRUCTOR(t):
    r'[A-Z][a-z_0-9A-Z]*(<[A-Z][a-z_0-9A-Z]*>)?\(([a-z_][a-z_0-9A-Z]*: ([A-Z][a-z_0-9A-Z]*(<[A-Z][a-z_0-9A-Z]*>)?)(,)?)*\)'
    t.value = str(t.value)
    t.type = reserved.get(t.value, 'CONSTRUCTOR')
    return t


def t_METHOD(t):
    r'\.[a-z_0-9A-Z]*'
    t.value = str(t.value)
    t.type = reserved.get(t.value, 'METHOD')
    return t


def t_CLASSNAME(t):
    r'[A-Z][a-z_0-9A-Z]*(<[A-Z][a-z_0-9A-Z]*>)?'
    t.value = str(t.value)
    t.type = reserved.get(t.value, 'CLASSNAME')
    return t


t_COMPAREOPERATOR = r'==|<=|>=|>|<|!='

t_LOGICOPERATOR = r'\|\||&&'

t_TYPIZATION = r':'

t_BLOCKSTART = r'\{'

t_BLOCKEND = r'\}'

t_PARSTART = r'\('

t_PAREND = r'\)'

t_EQUALITY = r'='

t_COMMA = r','

t_ARROW = r'\->'

t_ignore = ' \t'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


lexer = lex.lex()

f = open(sys.argv[1])

lexer.input(f.read())

while True:
    tok = lexer.token()
    if not tok:
        break
    print(tok)

test1List = ["LexToken(def,'def',1,0)",
             "LexToken(ID,'alphabetIntValence',1,4)",
             "LexToken(TYPIZATION,':',1,22)",
             "LexToken(CLASSNAME,'Alphabet<Int>',1,24)",
             "LexToken(EQUALITY,'=',1,38)",
             "LexToken(CLASSNAME,'Int',1,40)",
             "LexToken(METHOD,'.inRange',1,43)",
             "LexToken(PARSTART,'(',1,51)",
             "LexToken(INT,1,1,52)",
             "LexToken(COMMA,',',1,53)",
             "LexToken(INT,8,1,55)",
             "LexToken(PAREND,')',1,56)"
             ]


def test1():
    lexer.input("def alphabetIntValence: Alphabet<Int> = Int.inRange(1, 8)")
    i = 0
    while True:
        tok = lexer.token()
        if not tok:
            break
        if test1List[i] != str(tok):
            print("ERROR: " + str(tok))
        i = i+1


def test2():
    lexer.input("'a'")
    tok = lexer.token()
    if str(tok) != "LexToken(CHAR,'a',1,0)":
        print("ERROR: " + str(tok))

#
# test1()
# test2()

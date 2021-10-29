import enum
import sys
import ply.yacc as yacc
import logging

from lex import tokens


class ConstructorType(enum.Enum):
    enumeration = 0
    strict = 1
    describe = 2


class StateKind(enum.Enum):
    regular = 0
    start = 1
    terminal = 2


kind_to_string = {
    0: "regular",
    1: "start",
    2: "terminal"
}


class ProgramScope:
    def __init__(self, expressions):
        self.expressions = expressions

    def __str__(self):
        expr_str = ""
        for eee in self.expressions:
            expr_str += eee.__repr__()
            expr_str += "\n\n"

        return expr_str


class AutomatonKeyword(enum.Enum):
    kw_else = 0,
    kw_deadend = 1,
    kw_alphabet = 2


class Transition:
    def __init__(self, symbol_by, state_to):
        self.symbol_by = symbol_by
        self.state_to = state_to

    def __str__(self):
        return str(
            self.symbol_by.__str__() +
            " -> " +
            self.state_to.__str__()
        )


class AutomatonState:
    def __init__(self, name, kind, transitions):
        self.name = name
        self.kind = kind
        self.transitions = transitions

    def display(self, tabs):
        tabs_str = ""
        for i in range(tabs):
            tabs_str += "\t"

        result_str = ""
        for t in self.transitions:
            result_str += tabs_str
            result_str += t.__str__()

        return tabs_str + "Name: " + self.name.__str__() + "; Type: " + kind_to_string[self.kind] + "\n" + result_str


class Automaton:
    def __init__(self, name, alphabet_name, body):
        self.name = name
        self.alphabet_name = alphabet_name
        self.body = body

    def __repr__(self):
        states_str = ""
        for state in self.body.regular_states:
            states_str += "---\n"
            states_str += state.display(2)

        term_states_str = ""
        for state in self.body.terminal_states:
            term_states_str += "---\n"
            term_states_str += state.display(2)

        return str(
            "Automaton:\n\tname: " +
            self.name.__str__() + "\n\talphabet_name: " +
            self.alphabet_name.__str__() + "\n\tstart_state: " +
            self.body.start_state.display(2) + "regular_states:\n" +
            states_str + "\n\tterminal_states:\n" +
            term_states_str + "\n"
        )


class AutomatonBody:
    def __init__(self, start_state, regular_states, terminal_states):
        self.start_state = start_state
        self.regular_states = regular_states
        self.terminal_states = terminal_states


class Alphabet:
    def __init__(self, name, constructor_type, constructor_params):
        self.name = name
        self.constructor_type = constructor_type
        self.constructor_params = constructor_params

    def __repr__(self):
        params_str = ""
        if self.constructor_params is not None:
            for par in self.constructor_params:
                params_str += "\t\t"
                params_str += par.__repr__()
        else:
            params_str = "no constructor parameters given"

        return str(
            "Alphabet:\n\tname: " +
            self.name.__str__() + "\n\tconstructor_type: " +
            self.constructor_type.__str__() + "\n\tconstructor_params:\n" +
            params_str + "\n"
        )


class Variable:
    def __init__(self, vartype, constructor_params):
        self.vartype = vartype
        self.constructor_params = constructor_params

    def add_param(self, param):
        self.constructor_params.append(param)

    def __repr__(self):
        params_str = ""
        for par in self.constructor_params:
            params_str += "; "
            params_str += par.__str__()

        return str(
            "Variable:\tvartype:" +
            self.vartype.__str__() + "\tconstructor_params:\n" +
            params_str
        )


class ClassDefinition:
    def __init__(self, class_name, inherited_from, params, methods):
        self.class_name = class_name
        self.inherited_from = inherited_from
        self.params = params
        self.methods = methods

    def __repr__(self):
        params_str = ""
        for p in self.params:
            params_str += "\n\t\t"
            params_str += p.__str__()

        methods_str = ""
        for m in self.methods:
            methods_str += m.__repr__()

        return str(
            "ClassDefinition:\n\tclass_name: " + self.class_name.__str__() +
            "\n\tinherited_from: " + self.inherited_from.__str__() +
            "\n\tparams: " + params_str +
            "\n\tmethods:\n" + methods_str + "\n"
        )


class ClassField:
    def __init__(self, name, field_type, default_value):
        self.name = name
        self.field_type = field_type
        self.default_value = default_value

    def __repr__(self):
        return str(
            "{name: " + self.name.__str__() +
            " ; field_type: " + self.field_type.__str__() +
            " ; default_value: " + self.default_value.__str__() + " }"
        )


class ClassMethod:
    def __init__(self, name, fields, return_type, operations):
        self.name = name
        self.fields = fields
        self.return_type = return_type
        self.operations = operations

    def __repr__(self):
        fields_str = ""
        for f in self.fields:
            fields_str += "\n\t\t\t"
            fields_str += f.__str__()

        operations_str = ""
        for op in self.operations:
            operations_str += "\n\t\t\t"
            operations_str += op.__str__()

        return str(
            "\tClassMethod:\n\t\tname: " + self.name +
            "\n\t\tfields: " + fields_str +
            "\n\t\treturn_type: " + self.return_type.__str__() +
            "\n\t\toperations: " + operations_str
        )


class FieldAccess:
    def __init__(self, belongs_to, field_name):
        self.belongs_to = belongs_to
        self.name = field_name

    def __str__(self):
        return str(
            "{belongs_to: " + self.belongs_to.__str__() +
            " ; field_name: " + self.name + " }"
        )


class CompareOperation:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __str__(self):
        return str(
            "{left: " + self.left.__str__() +
            " ; operator: " + self.operator.__str__() +
            " ; right: " + self.right.__str__() + " }"
        )


def p_expressions(p):
    '''expressions : expression
                   | expression expressions'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        if len(p) == 3:
            p[0] = [p[1]] + p[2]


def p_expression(p):
    '''expression : classdef
                  | automaton
                  | alphabet
                  '''
    p[0] = p[1]


def p_empty(p):
    'empty :'
    p[0] = []


def p_error(p):
    print("Syntax error")


def p_alphabet(p):
    '''alphabet : DEF ID TYPIZATION CLASSNAME EQUALITY BLOCKSTART enumeration BLOCKEND
                | DEF ID TYPIZATION CLASSNAME EQUALITY CLASSNAME METHOD PARSTART enumeration PAREND
                | DEF ID TYPIZATION CLASSNAME EQUALITY CLASSNAME METHOD BLOCKSTART alphabetdescribebody BLOCKEND
                 '''
    if len(p) == 9:
        p[0] = Alphabet(p[2], ConstructorType.enumeration, p[7])
    else:
        if len(p) == 11:
            if p[8] == "(":
                p[0] = Alphabet(p[2], ConstructorType.strict, p[9])
            else:
                if p[8] == "{":
                    p[0] = Alphabet(p[2], ConstructorType.describe, p[9])


def p_enumeration(p):
    '''enumeration : term
                   | term COMMA enumeration
                   '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]
    # print(p[0])


def p_term(p):
    '''term : CHAR
            | INT
            | STRING
            | ID
            | CLASSNAME PARSTART enumeration PAREND
            '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        if len(p) == 5:
            p[0] = Variable(p[1], p[3])


def p_alphabetdescribebody(p):
    '''alphabetdescribebody : paramsdescribe
                            | paramsdescribe COMMA alphabetdescribebody
                            '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        if len(p) == 4:
            p[0] = [p[1]] + p[2]


def p_paramsdescribe(p):
    'paramsdescribe : enumeration FROM ID'
    p[0] = p[1], p[3]


def p_transitionterm(p):
    '''transitionterm : CHAR
                      | INT
                      | STRING
                      | CLASSNAME PARSTART enumeration PAREND
                      '''
    if len(p) == 2:
        p[0] = Variable(type(p[1]).__name__, p[1])
    else:
        if len(p) == 5:
            p[0] = Variable(p[1], p[3])


def p_transitionkeyword(p):
    '''transitionkeyword : ELSE
                         | DEADEND
                         | ALPHABET
                         | ITSELF
                         '''
    p[0] = p[1]


def p_transition(p):
    '''transition : transitionterm ARROW ID
                  | transitionkeyword ARROW ID
                  | transitionkeyword ARROW transitionkeyword
                  '''
    p[0] = Transition(p[1], p[3])


def p_automaton(p):
    'automaton : DEF ID TYPIZATION CLASSNAME EQUALITY CLASSNAME METHOD PARSTART ID PAREND METHOD BLOCKSTART automatondescribebody BLOCKEND'
    p[0] = Automaton(p[2], p[9], p[13])


def p_automatondescribebody(p):
    'automatondescribebody : START statedescription states TERMINAL BLOCKSTART termstates BLOCKEND'
    p[0] = AutomatonBody(AutomatonState(name="start", kind=StateKind.start, transitions=p[2]), p[3], p[6])


def p_statedescription(p):
    '''statedescription : transition statedescription
                        | transition
                        '''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        if len(p) == 2:
            p[0] = [p[1]]


def p_states(p):
    '''states : states ID statedescription
              | ID statedescription
              | empty
              '''
    if len(p) == 4:
        p[0] = p[1] + [(AutomatonState(name=p[2], kind=StateKind.regular, transitions=p[3]))]
    else:
        if len(p) == 3:
            p[0] = [AutomatonState(name=p[1], kind=StateKind.regular, transitions=p[2])]
        else:
            p[0] = []


def p_termstates(p):
    '''termstates : termstates ID statedescription
                  | ID statedescription
                  | empty
                  '''
    if len(p) == 4:
        p[0] = p[1] + [(AutomatonState(name=p[2], kind=StateKind.terminal, transitions=p[3]))]
    else:
        if len(p) == 3:
            p[0] = [AutomatonState(name=p[1], kind=StateKind.terminal, transitions=p[2])]
        else:
            p[0] = []


def p_classdef(p):
    'classdef : CLASS CLASSNAME PARSTART fields PAREND TYPIZATION CLASSNAME BLOCKSTART classbody BLOCKEND'
    p[0] = ClassDefinition(class_name=p[2], inherited_from=p[7], params=p[4], methods=p[9])


def p_field(p):
    '''field : ID TYPIZATION CLASSNAME
             | ID TYPIZATION CLASSNAME EQUALITY transitionterm
             '''
    if len(p) == 4:
        p[0] = ClassField(name=p[1], field_type=p[3], default_value=None)
    else:
        p[0] = ClassField(name=p[1], field_type=p[3], default_value=p[5])


def p_fields(p):
    '''fields : field
              | field COMMA fields
              '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]


def p_classbody(p):
    '''classbody : method
                 | method classbody
                 '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[2].insert(0, p[1])


def p_method(p):
    'method : OVERRIDE FUN ID PARSTART fields PAREND TYPIZATION CLASSNAME BLOCKSTART RETURN PARSTART logicoperations PAREND BLOCKEND'
    p[0] = ClassMethod(name=p[3], fields=p[5], return_type=p[8], operations=p[12])


def p_compareoperation(p):
    'compareoperation : ID METHOD COMPAREOPERATOR ID METHOD'
    p[0] = CompareOperation(FieldAccess(p[1], p[2]), p[3], FieldAccess(p[4], p[5]))


def p_logicoperations(p):
    '''logicoperations : compareoperation
                       | PARSTART logicoperations PAREND
                       | logicoperations LOGICOPERATOR PARSTART compareoperation PAREND
                       '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        if len(p) == 4:
            p[0] = [p[1]] + p[2] + [p[3]]
        else:
            if len(p) == 6:
                p[0] = p[1] + [p[2], p[3], p[4], p[5]]


# Set up a logging object
logging.basicConfig(
    level=logging.DEBUG,
    filename="parselog.txt",
    filemode="w",
    format="%(filename)10s:%(lineno)4d:%(message)s"
)
log = logging.getLogger()

# lex.lex(debug=True, debuglog=log)

start = 'expressions'
parser = yacc.yacc(debug=True, debuglog=log)

sys.stdin = open(sys.argv[1], 'r')
sys.stdout = open(sys.argv[1] + '.out', 'w')

result = parser.parse(sys.stdin.read())
print(result.__str__())

# ----------------------------
# PRÉ ANÁLISE LEXICA
# ----------------------------
import string

delimiters = ["(", ")", "{", "}", "[", "]", ";", ",", "<<", ">>", "do", "end"]
tokens_dict = {}
reserved_words = ["feature", "none", "assign", "current", "create", "class",
                  "loop", "from", "until", "all", "some", "integer", "array"]
operators = ["=", "/=", "<", ">", "<=", ">=", "+", "-", "not",
             "*", "/", "//", "^", "and", "or", ":=", "assign", ":", "."]


# ----------------------------
# MÁQUINA DE ESTADOS GENÉRICA
# ----------------------------


class MEG:
    def __init__(self, states, events, initialState, acceptanceStates):
        if type(acceptanceStates) != list:
            acceptanceStates = [acceptanceStates]

        self.states = states
        self.events = events
        self.currentState = initialState
        self.acceptanceStates = acceptanceStates

        if (initialState not in states):
            states.append(initialState)

        if ("err" not in states):
            states.append("err")

        self.transitionTable = {}
        for state in states:
            self.transitionTable[state] = {}
            for event in events:
                self.transitionTable[state][event] = "err"

    def setTransitionRule(self, originState, events, targetState):
        if ((originState not in self.states) or (targetState not in self.states)):
            return

        if (type(events) != list):
            events = [events]

        for event in events:
            if (event in self.events):
                self.transitionTable[originState][event] = targetState

    def gotoNextState(self, event):
        if ((event not in self.events) or (self.currentState not in self.states)):
            self.currentState = "err"
            return "err"

        self.currentState = self.transitionTable[self.currentState][event]
        return self.currentState

    def recognizes(self):
        return self.currentState in self.acceptanceStates


# ----------------------------
# FUNÇÕES BÁSICAS
# ----------------------------


def loadSourceCode(path="code.txt"):
    with open(path, "r") as source:
        return source.read()


def addNewToken(lexeme, lexeme_class):
    if lexeme in tokens_dict.keys():
        return

    tokens_dict[lexeme] = lexeme_class


def throwError(error_position, error_message):
    print(f'An error has be found in position {error_position}.')
    print(f'See description: {error_message}')


# ----------------------------
# AUTOMATOS RECONHECEDORES
# ----------------------------


def recognizesInteger(stack):
    states = ["q0", "qf"]
    sign_events = ["+", "-"]
    digit_events = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    meg = MEG(states, sign_events+digit_events, "q0", "qf")
    meg.setTransitionRule("q0", sign_events+digit_events, "qf")
    meg.setTransitionRule("qf", digit_events, "qf")

    for char in stack:
        meg.gotoNextState(char)

    return meg.recognizes()


def recognizesReserved(stack):
    return stack in reserved_words


def classifiesToken(stack):
    if(recognizesInteger(stack)):
        addNewToken(stack, "int")
    elif(recognizesReserved(stack)):
        addNewToken(stack, "reserved")
    else:
        addNewToken(stack, "id")


def commentsRecognizer(stack):

    # Ver a questao dos caracteres

    states = ['q0', 'qint', 'qf']
    digit_events = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    alphabet_events = list(string.ascii_lowercase)
    # aqui tem que ser o -, osd igitos e o alfabeto
    events = ['\n', ' ']+digit_events+alphabet_events
    meg = MEG(states, events+['-'], "q0", "qf")
    meg.setTransitionRule('q0', ['-'], 'qint')
    meg.setTransitionRule('qint', '-', 'qf')
    meg.setTransitionRule('qf', events, 'qf')

    for char in stack:
        meg.gotoNextState(char)

    return meg.recognizes()


def delimitersRecognizer(stack):
    states = ['q0', 'qf', 'qintmenor', 'qintmaior']
    delimitersOneDigit = delimiters[:8]
    events = delimitersOneDigit+[' ', '\n', '>', "<"]
    meg = MEG(states, events, 'q0', 'qf')

    # >> e <<
    meg.setTransitionRule('q0', '>', 'qintmaior')
    meg.setTransitionRule('qintmaior', '>', 'qf')
    meg.setTransitionRule('q0', '<', 'qintmenor')
    meg.setTransitionRule('qintmenor', '<', 'qf')

    # delimitadores com um unico digito, logo vai pro final
    meg.setTransitionRule('q0', delimitersOneDigit, 'qf')

    for char in stack:
        meg.gotoNextState(char)

    return meg.recognizes()


def operatorsRecognizer(stack):

    states = ['q0', 'qf', 'qintdivide', 'qintmenor', 'qintmaior', 'qintpontos']
    events = operators+[" ", '\n']
    meg = MEG(states, events, 'q0', 'qf')

    meg.setTransitionRule('q0', ["=", "+", "-", "*", "^", "."], 'qf')
    meg.setTransitionRule('q0', ['/'], 'qf')
    meg.setTransitionRule('qf', ['/', '='], 'qf')

    meg.setTransitionRule('q0', ['<'], 'qf')
    meg.setTransitionRule('qf', ['=', ""], 'qf')

    meg.setTransitionRule('q0', ['>'], 'qf')
    meg.setTransitionRule('qf', ['=', ""], 'qf')

    meg.setTransitionRule('q0', [':'], 'qf')
    meg.setTransitionRule('qf', ['=', ""], 'qf')

    for char in stack:
        meg.gotoNextState(char)

    return meg.recognizes()


# Separators

def hierarchy(stream, level):
    if level == 0:
        comments_separator(stream)
    elif level == 1:
        op_separator(stream)
    elif level == 2:
        delimiters_separator(stream)
    elif level == 3:
        classifiesToken(stream)


def comments_separator(stream):

    # se tiver um comentario, ele vai ignorar de -- ate o fim da linha
    word = ""
    for index, char in enumerate(stream):
        if index != (len(stream)-1):
            combination = char+stream[index+1]
            if commentsRecognizer(combination):
                # reconheceu, lgo descarta o resto
                word = stream[0:index]
                break
            else:
                word += char
        else:
            word += char
    hierarchy(word, 1)


def op_separator(stream):
    # operator ta comendo o << e >> quando manda pra o delimiter

    index = 0
    word = ""
    while index != len(stream):

        char = stream[index]
        if operatorsRecognizer(char):
            # reconheceu, testar para o proximo
            operatorLexeme = char
            if index != len(stream)-1:

                nextCharStream = char+stream[index+1]

                if operatorsRecognizer(nextCharStream):
                    # operator composto
                    operatorLexeme = nextCharStream
                    index += 1

                elif delimitersRecognizer(nextCharStream):
                    # eh um delimitador, nao aceitar
                    operatorLexeme = ""
                    word += nextCharStream
                    index += 1

            # mandar para a hierarquia o que ele ja achou
            if operatorLexeme != "":
                addNewToken(operatorLexeme, "opr")
                operatorLexeme = ""

            hierarchy(word, 2)
            index += 1
            word = ""

        else:
            # nao reconheceu o atual, continua procurando
            # ja vem sem os comentarios e espaço em branco
            word += char
            index += 1
    hierarchy(word, 2)


def delimiters_separator(stream):

    index = 0
    word = ""
    while index != len(stream):

        char = stream[index]

        if char in ["<", ">"]:

            # reconheceu, testar para o proximo
            delimiterLexeme = char

            if index != len(stream)-1:

                nextCharStream = char+stream[index+1]

                if delimitersRecognizer(nextCharStream):
                    # delimiter composto
                    delimiterLexeme = nextCharStream
                    index += 1
                    addNewToken(delimiterLexeme, "del")

                    # se nao for, é simples, logo, nao é delimitador

            delimiterLexeme = ""
            index += 1
            hierarchy(word, 3)
            word = ""
        elif char in delimiters:
            index += 1
            addNewToken(char, "del")
        else:
            # nao reconheceu o atual, continua procurando
            # ja vem sem os comentarios e espaço em branco
            word += char
            index += 1

# ----------------------------
# TESTES UNITARIOS
# ----------------------------


def printTest(title, tests):
    print(f'Unit Testing: {title}')
    for resultKey, resultValue in tests.items():
        print(f'    [{ "🟢" if (resultValue) else "🔴"}] {resultKey}')


def testIntegerRecognizer():
    tests = {
        "acceptsUnsignedInt": recognizesInteger("123"),
        "acceptsSignedPositiveInt": recognizesInteger("+123"),
        "acceptsSignedNegativeInt": recognizesInteger("-123"),
        "rejectsLettersInTheStart": not recognizesInteger("AB3456"),
        "rejectsLettersInTheMiddle": not recognizesInteger("12CD56"),
        "rejectsLettersInTheEnd": not recognizesInteger("1234EF"),
        "rejectsSingleLetterInTheStart": not recognizesInteger("X23"),
        "rejectsSingleLetterInTheMiddle": not recognizesInteger("1Y3"),
        "rejectsSingleLetterInTheEnd": not recognizesInteger("12Z")
    }
    printTest("IntegerRecognizer", tests)


def testReservedRecognizer():
    tests = {
        "acceptsClass": recognizesReserved("class"),
        "acceptsFeature": recognizesReserved("feature"),
        "rejectsHello": not recognizesReserved("hello")
    }
    printTest("ReservedRecognizer", tests)


def testCommentsRecognizer():
    tests = {
        "acceptsComments": commentsRecognizer("-- 123asdad")
    }
    printTest("CommentsRecognizer", tests)


def testDelimitersRecognizer():
    tests = {
        "acceptsDelimitersSingle": delimitersRecognizer(">"),
        "acceptsDelimitersDouble": delimitersRecognizer(">>"),
        "acceptsDelimitersWrong": delimitersRecognizer("\s")
    }
    printTest("DelimitersRecognizer", tests)


def testOperatorsRecognizer():
    tests = {
        "acceptsOperatorsTwoRight": operatorsRecognizer("//"),
        "acceptsOperatorsTwoWrong": operatorsRecognizer("/-"),
        "acceptsOperatorsTwoWrong2": operatorsRecognizer("/a"),
        "acceptsOperators": operatorsRecognizer(">>")
    }
    printTest("CommentsRecognizer", tests)


# ----------------------------
# LOOP PRINCIPAL
# ----------------------------


def main():
    source_code = loadSourceCode()
    lines = source_code.split("\n")

    for line in lines:
        hierarchy(line, 0)
    print(tokens_dict)


if __name__ == '__main__':
    # testIntegerRecognizer()
    # testOperatorsRecognizer()
    # testDelimitersRecognizer()
    # testReservedRecognizer()
    main()

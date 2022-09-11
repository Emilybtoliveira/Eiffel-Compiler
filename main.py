# ----------------------------
# PRÉ ANÁLISE LEXICA
# ----------------------------


delimiters = ["(", ")", "{", "}", "[", "]", ";", ",", "<<", ">>", "do", "end"]
tokens_dict = {}
reserved_words = ["feature", "none", "assign", "current", "create",
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
    # print(tokens_dict)


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
    tests.items()
    printTest("IntegerRecognizer", tests)


# ----------------------------
# LOOP PRINCIPAL
# ----------------------------


def main():
    source_code = loadSourceCode()

    # ordem de chamada dos reconhecedores
    # TODO: commentsRecognizer()
    # TODO: delimitersRecognizer()
    # TODO: operatorsRecognizer()
    # TODO: idRecognizer()  # aqui verifica-se se é uma palavra reservada
    # DONE: integerRecognizer()


if __name__ == '__main__':
    testIntegerRecognizer()
    main()

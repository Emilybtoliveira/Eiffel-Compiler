""" PRÉ ANÁLISE LEXICA """

# adicionar aqui os tokens que vao ser do tipo ["lexema" : "classe"].
delimiters = ["(", ")", "{", "}", "[", "]", ";", ",", "<<", ">>", "do", "end"]
tokens_dict = {}
reserved_words = ["feature", "none", "assign", "current", "create",
                  "loop", "from", "until", "all", "some", "integer", "array"]
operators = ["=", "/=", "<", ">", "<=", ">=", "+", "-", "not",
             "*", "/", "//", "^", "and", "or", ":=", "assign", ":", "."]


""" FUNÇÕES BÁSICAS """


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


""" LOOP PRINCIPAL """


def main():
    source_code = loadSourceCode()

    # ordem de chamada dos reconhecedores
    # TODO: commentsRecognizer()
    # TODO: delimitersRecognizer()
    # TODO: operatorsRecognizer()
    # TODO: idRecognizer()  # aqui verifica-se se é uma palavra reservada
    # TODO: constantRecognizer()


if __name__ == '__main__':
    main()

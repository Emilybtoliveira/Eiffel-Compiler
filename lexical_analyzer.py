from calendar import c
from curses.ascii import isdigit
from lib2to3.pgen2 import token
import string
from dataclasses import dataclass

# ============ ESTRUTURAS DE DADOS ============


@dataclass()
class Token:
    lexeme: string
    lexeme_class: string


current_position = 0
line_count = 0
source_code = ""
tokens_list: list[Token] = []

delimiters = ["(", ")", "[", "]", ",", "<<", ">>"]
reserved_words = ["feature", "create", "class", "integer", "loop", "from",
                  "until", "array", "do", "end", "not", "and", "or", "if", "then", "else"]
operators = ["=", "/=", "<", ">", "<=", ">=",
             "+", "-", "*", "/", "//", "^", ":=", ":", "."]

# ============ RECONHECEDORES ============


def checksNewLineAndSpace():
    global current_position, line_count

    while (source_code[current_position] == "\n" or source_code[current_position] == " "):
        if source_code[current_position] == "\n":
            line_count += 1
            #print(f"linha {line_count}")

        current_position += 1

        if current_position >= len(source_code):
            break


def commentRecognizer():
    global current_position
    #print("Iniciando reconhecedor de comentarios...")
    lexeme = ""

    checksNewLineAndSpace()

    if current_position+1 < len(source_code):
        if source_code[current_position] == "-" and source_code[current_position+1] == "-":
            lexeme += "--"
            current_position += 2

            while (source_code[current_position] != "\n"):
                lexeme += source_code[current_position]
                current_position += 1

                if current_position >= len(source_code):
                    break

            new_token = Token(lexeme, "comment")
            # print(f"{new_token}")
            tokens_list.append(new_token)

            return True

    return False


def delimiterRecognizer():
    global current_position
    #print("Iniciando reconhecedor de delimitadores...")
    lexeme = ""

    checksNewLineAndSpace()

    if source_code[current_position] in delimiters:
        lexeme += source_code[current_position]
        current_position += 1
    elif current_position+1 < len(source_code):
        if (source_code[current_position]+source_code[current_position+1]) in delimiters:
            lexeme += source_code[current_position] + \
                source_code[current_position+1]
            current_position += 2
        else:
            return False
    else:
        return False

    new_token = Token(lexeme, "del")
    # print(f"{new_token}")
    tokens_list.append(new_token)
    return True


def operatorRecognizer():
    global current_position
    #print("Iniciando reconhecedor de operadores...")
    lexeme = ""

    checksNewLineAndSpace()

    if current_position+1 < len(source_code):
        if (source_code[current_position]+source_code[current_position+1]) in operators:
            lexeme += source_code[current_position] + \
                source_code[current_position+1]

            current_position += 2
            new_token = Token(lexeme, "opr")
            # print(f"{new_token}")
            tokens_list.append(new_token)

            return True

    if source_code[current_position] in operators:
        lexeme += source_code[current_position]

        current_position += 1
        new_token = Token(lexeme, "opr")
        # print(f"{new_token}")
        tokens_list.append(new_token)

        return True
    else:
        return False


def numberRecognizer():
    global current_position
    #print("Iniciando reconhecedor de números...")
    lexeme = ""

    checksNewLineAndSpace()

    if ord(source_code[current_position]) >= 48 and ord(source_code[current_position]) <= 57:
        while ord(source_code[current_position]) >= 48 and ord(source_code[current_position]) <= 57:
            lexeme += source_code[current_position]
            current_position += 1

            if current_position >= len(source_code):
                break

        new_token = Token(lexeme, "int")
        # print(f"{new_token}")
        tokens_list.append(new_token)
        return True
    return False


def identifierRecognizer():
    global current_position
    #print("Iniciando reconhecedor de identificadores...")
    lexeme = ""

    checksNewLineAndSpace()

    if (ord(source_code[current_position]) >= 97 and ord(source_code[current_position]) <= 122) or (ord(source_code[current_position]) >= 65 and ord(source_code[current_position]) <= 90):
        while (ord(source_code[current_position]) >= 97 and ord(source_code[current_position]) <= 122) or (ord(source_code[current_position]) >= 65 and ord(source_code[current_position]) <= 90):
            lexeme += source_code[current_position]
            current_position += 1

            if current_position >= len(source_code):
                break

        if lexeme.lower() in reserved_words:
            new_token = Token(lexeme, "reserved")
        else:
            new_token = Token(lexeme, "id")
        # print(f"{new_token}")
        tokens_list.append(new_token)
        return True

    return False

# ============ FUNÇÕES GERAIS ============


def throwError():
    global current_position, line_count

    print(f'An error has been found in line {line_count+1}.')
    print(
        f'See description: Word {source_code[current_position]} not recognized.\n')
    current_position += 1


def loadSourceCode():
    with open("code.txt", "r") as source:
        return source.read()


def iterativeScanner(source_code):

    try:
        for i in range(len(source_code)):

            if not commentRecognizer():
                #print("Não é comentário.")

                if not delimiterRecognizer():
                    #print("Não é delimitador.")

                    if not operatorRecognizer():
                        #print("Não é operador.")

                        if not numberRecognizer():
                            #print("Não é número.")

                            if not identifierRecognizer():
                                #print("Não é identificador.")

                                throwError()
    except IndexError:
        return ()


def printTokens():
    output = ""
    for token in tokens_list:
        output = output + str(token) + "\n"
        print(token)

    with open("tokens.txt", "w") as source:
        return source.write(output)


def resetGlobals():
    global source_code, current_position, line_count, tokens_list
    source_code = ""
    current_position = 0
    line_count = 0
    tokens_list = []


def parseLine(line):
    resetGlobals()
    global source_code

    source_code = line
    iterativeScanner(source_code)

    classToToken, tokenToClass = {}, {}
    for t in tokens_list:
        if t.lexeme_class not in classToToken.keys():
            classToToken[t.lexeme_class] = []
        classToToken[t.lexeme_class].append(t.lexeme)
        tokenToClass[t.lexeme] = t.lexeme_class

    return tokens_list


def main(debug=False, code: str = None):
    resetGlobals()
    global source_code

    try:
        source_code = code if code != None else loadSourceCode()
    except:
        print("\nErro: Não foi possível ler o arquivo.")
    else:
        iterativeScanner(source_code)
        if debug:
            printTokens()

        return tokens_list


if __name__ == '__main__':
    main(True)

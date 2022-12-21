from lexical_analyzer import parseLine, Token
from syntax_analyzer import main as syntax, Simbolo
from dataclasses import dataclass
from copy import deepcopy as copy


@dataclass
class Node:
    content: str
    type: str
    left: 'Node'
    right: 'Node'
    leaf: bool = True


def printTable(table: dict[Simbolo]):
    print("\n--------------------------------------------------------------------------")
    print("|       lexema       |   tipo   | tipoDeRetorno | valor | escopo | idRec |")

    for key, simbolo in table.items():
        print("--------------------------------------------------------------------------")
        print(
            f"|{str(simbolo.lexema).center(20)}|{str(simbolo.tipo).center(10)}|{str(simbolo.retornotipo).center(15)}|{str(simbolo.valor).center(7)}|{str(simbolo.escopo).center(8)}|{str(simbolo.idrec).center(7)}|")

    print("--------------------------------------------------------------------------")


def generateTreeString(node: Node, depth: int):
    nodeStr = ""
    if (depth != 0):
        for _ in range(depth):
            nodeStr += "    "
        nodeStr += "|\n"
    for _ in range(depth):
        nodeStr += "    "
    nodeStr += "\""+node.content+"\"\n"

    childStrs = []
    for child in (node.left, node.right):
        if (child != None):
            depth += 1
            childStrs.append(generateTreeString(child, depth))
            depth -= 1

    for string in childStrs:
        nodeStr += string
    return nodeStr


def expressionParser(term: str, tokensList: list[Token]) -> Node:
    operator, op1, op2 = "", "", ""

    noDelList = [i for i in tokensList if i.lexeme_class != "del"]
    if (len(noDelList) == 1):
        return Node(noDelList[0].lexeme, noDelList[0].lexeme_class, None, None)

    nP = 0
    if (term[0] == "("):
        term = term.replace("(", "", 1)
        term = term.replace(")", "", 1)

    if (term[-1] == ")"):
        termR = term[::-1]
        termR = termR.replace("(", "", 1)
        termR = termR.replace(")", "", 1)
        term = termR[::-1]

    for index, token in enumerate(tokensList):
        if token.lexeme == "(":
            nP += 1
        if token.lexeme == ")":
            nP -= 1

        if token.lexeme_class == "opr" and nP <= 1:
            operator = token.lexeme
            splitted = term.split(operator)

            op1TL = tokensList[:index]
            op1Term = splitted.pop(0)

            op2TL = tokensList[index+1:]

            op2Term = operator.join(splitted)

            op1 = expressionParser(op1Term, op1TL)
            op2 = expressionParser(op2Term, op2TL)
            return Node(operator, "opr", op1, op2, False)


def evalExpressionTree(expressionRoot: Node, table):
    pass


def handleExpression(line: str, tokensList: list[Token], table: dict[Simbolo]):
    line = line.replace(" ", "")
    target, value = line.split(":=")

    index = 0
    while index < len(tokensList):
        token = tokensList[index]
        if (token.lexeme == target):
            target = token
            del tokensList[index]
            index -= 1
        elif (token.lexeme == ":="):
            del tokensList[index]
            index -= 1
            break
        index += 1

    expressionRoot = expressionParser(value, tokensList)
    textTree = generateTreeString(expressionRoot, 0)
    #print(textTree)

    valueTest = value.replace("/=", "!=")
    for tN, token in table.items():
        valueTest = valueTest.replace(tN, str(token.valor))
    if (target.lexeme not in table.keys()):
        table[target.lexeme] = Simbolo(
            target.lexeme, "var", "INTEGER", int(eval(valueTest)), "local", 0)
    else:
        table[target.lexeme].valor = int(eval(valueTest))

    return table


def handleAttribution(line: str, tokensList: list[Token], table):
    line = line.replace(" ", "")
    target, value = line.split(":")

    valueTest = value.replace("/=", "!=")
    for tN, token in table.items():
        valueTest.replace(tN, token.valor)
    table[target] = Simbolo(target, "var", "INTEGER",
                            int(eval(valueTest)), "local")
    return table


def loadSourceCode():
    with open("code.txt", "r") as source:
        return source.read()


@dataclass
class method:
    name: str
    returnType: str
    body: str
    params: list[Simbolo]


def selectOne(methods: dict[method]):
    options = []
    i = 0
    for m in methods.values():
        options.append(m)
        print(f"[{i}] - ", m.name)
        i += 1

    s = input("Digite o número da opção desejada: ")
    while ((not s.isdigit()) or (s.isdigit() and int(s) < 0 and int(s) >= len(methods.keys()))):
        s = input("Selecione uma opção válida: ")

    return options[int(s)]


def request(param: Simbolo):
    s = input(f"Digite o valor para atribuir ao parâmetro {param.lexema}: ")

    if (not s.isdigit()):
        print("Parâmetro inválido, deveria ser número inteiro.")

    return s


def main():
    methods = {}
    params = {}

    entryTable: list[Simbolo] = syntax(show=False)
    gTable = dict()

    for simbolo in entryTable:
        if (simbolo.tipo == "method"):
            methods[simbolo.lexema] = method(
                simbolo.lexema, simbolo.retornotipo, simbolo.body, [])
        elif (simbolo.tipo == "param"):
            if not (simbolo.escopo in params.keys()):
                params[simbolo.escopo] = []
            params[simbolo.escopo].append(simbolo)
        elif (simbolo.tipo == "var"):
            gTable[simbolo.lexema] = simbolo

    for pName, p in methods.items():
        if (pName not in params.keys()):
            params[pName] = []
        p.params = params[pName]

    while True:

        print("#############################################\n")
        lTable = copy(gTable)
        proc: method = selectOne(methods)
        for param in proc.params:
            lTable[param.lexema] = Simbolo(param.lexema, param.tipo, param.retornotipo,
                                           request(param), "local", 0)
        print("\n#############################################\n")
        print(f"\n>>>> {proc.name}'s local table\n")
        printTable(lTable)
        for line in list(filter(lambda line: line != "", proc.body.split("\n"))):
            classToTokens, tokenToClass, tokensList = parseLine(line)
            print()
            if ":=" in classToTokens.get("opr", []):
                lTable = handleExpression(line, tokensList, lTable)
                print("(Expression)")
            elif ":" in classToTokens.get("opr", []):
                lTable = handleAttribution(line, tokensList, lTable)
                print("(Variable Declaration)")
            print(line, "\n")
            printTable(lTable)
            print("\n")

        if (lTable.get("Result", None) != None):
            print("\nReturning value ", lTable["Result"].valor)
        print("\n")

        for lexame, simbolo in gTable.items():
            if (lTable[lexame].escopo == "global"):
                gTable[lexame] = lTable[lexame]
        print("\n#############################################\n")
        print(f"Execução de {proc.name} resultou na tabela global:")
        printTable(gTable)
        print()


if __name__ == "__main__":
    main()

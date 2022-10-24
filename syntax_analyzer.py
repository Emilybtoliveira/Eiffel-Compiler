from curses.ascii import isalnum
from dataclasses import dataclass
import string
from typing import List
import lexical_analyzer

# =========== ESTRUTURAS DA TABELA DE ANALISE =========================

initial_non_terminal = "<class_declaration>"
productions_table = {"<class_declaration>": {"class": ["<class_header>","<creation_instruction>", "<features>", "end"]},
                    "<class_header>": {"class": ["class", "<class_name>"],}, 
                    "<class_name>": {"<identifier>": ["<identifier>"]},
                    "<features>": {"end": [], "feature": ["<feature_clause>", "<features>"]},
                    "<feature_clause>": {"feature": ["feature", "<feature_declaration_list>"]},
                    "<feature_declaration_list>": {"end": [], "feature":[], "<identifier>":["<feature_declaration>", "<feature_declaration_list>"]},
                    "<feature_declaration>": {"<identifier>": ["<feature_name>", "<declaration_body>"]},
                    "<feature_name>": {"<identifier>":["<identifier>"]},
                    "<declaration_body>": {":=":["<formal_arguments>", "<argument_type_mark>", "<feature_value>"], ":":["<formal_arguments>", "<argument_type_mark>", "<feature_value>"],
                        "(":["<formal_arguments>", "<argument_type_mark>", "<feature_value>"], "do":["<formal_arguments>", "<argument_type_mark>", "<feature_value>"],
                        "<identifier>": ["<formal_arguments>", "<argument_type_mark>", "<feature_value>"]},
                    "<formal_arguments>":{":=": [], ":": [], "(": ["(", "<entity_declaration_list>", ")"], "do": [], "<identifier>": []},
                    "<entity_declaration_list>": {"<identifier>": ["<entity_declaration_group>", "<entity_declaration_list_e>"]},
                    "<entity_declaration_list_e>": {")": [], ",": [",", "<entity_declaration_list>"]},
                    "<entity_declaration_group>": {"<identifier>": ["<identifier_list>", "<type_mark>"]},
                    "<identifier_list>": {"<identifier>": [["<identifier>", ",", "<identifier_list>"], ["<identifier>"]]},
                    "<type_mark>": {":": [":", "<type>"]},
                    "<argument_type_mark>": {":=": [], ":": [":", "<type>"], "do": [], "<identifier>": []},
                    "<type>": {"ARRAY": ["ARRAY", "[", "<type>", "]"], "INTEGER": ["INTEGER"], "<identifier>": ["<class_name>"]},
                    "<feature_value>": {":=": ["<explicit_value>", "<attribute_or_routine>"], "do": ["<explicit_value>", "<attribute_or_routine>"], "<identifier>": []},
                    "<explicit_value>": {":=": [":=", "<manifest_constant>"], "do":  []},
                    "<attribute_or_routine>": {"do": ["do", "<compound>", "end"], "<identifier>": []},
                    "<compound>": {"+": ["<instruction>", "<compound>"], "-": ["<instruction>", "<compound>"], "(": ["<instruction>", "<compound>"], "[": ["<instruction>", "<compound>"], "end": [], "create": ["<instruction>", "<compound>"], 
                        "loop": ["<instruction>", "<compound>"], "from": ["<instruction>", "<compound>"], "until": [], "if": ["<instruction>", "<compound>"], "else": [], "not": ["<instruction>", "<compound>"], "<identifier>": ["<instruction>", "<compound>"]}, 
                    "<instruction>": {"(": ["<call>"], "create": ["<creation_expression>"], "loop": ["<loop>"], "from": ["<loop>"], "until": ["<loop>"], 
                        "if": ["<conditional>"], "<identifier>": [["<call>"], ["<assigner_call>"]]}, 
                    "<assigner_call>": {"<identifier>": ["<variable>", ":=", "<expression>"]},
                    "<manifest_constant>": {"+": ["<manifest_type>", "<manifest_value>"], "-": ["<manifest_type>", "<manifest_value>"], "<integer>": ["<manifest_type>", "<manifest_value>"]},
                    "<manifest_type>": {"+": [], "-": [], "<<": [], "ARRAY": ["<type>"], "INTEGER": ["<type>"], "<identifier>": ["<type>"], "<integer>": []}, 
                    "<manifest_value>": {"+": ["<sign>", "<integer>"], "-": ["<sign>", "<integer>"], "<integer>": ["<sign>", "<integer>"]},
                    "<manifest_value_bracket>": {"+": ["<sign>", "<integer>"], "-": ["<sign>", "<integer>"], "]": [], "<integer>": ["<sign>", "<integer>"]},
                    "<manifest_array>": {"<<": ["<manifest_type>", "<<", "<expression_list>", ">>"], "ARRAY": ["<manifest_type>", "<<", "<expression_list>", ">>"], "INTEGER": ["<manifest_type>", "<<", "<expression_list>", ">>"],
                        "<identifier>": ["<manifest_type>", "<<", "<expression_list>", ">>"]}, 
                    "<expression_list>": {"+": [["<expression>", ",", "<expression_list>"], ["<expression>"]], "-": [["<expression>", ",", "<expression_list>"], ["<expression>"]], "(": [["<expression>", ",", "<expression_list>"], ["<expression>"]], 
                        "[": [["<expression>", ",", "<expression_list>"], ["<expression>"]], "<<": [["<expression>", ",", "<expression_list>"], ["<expression>"]], "if": [["<expression>", ",", "<expression_list>"], ["<expression>"]], 
                        "ARRAY": [["<expression>", ",", "<expression_list>"], ["<expression>"]], "INTEGER": [["<expression>", ",", "<expression_list>"], ["<expression>"]], "not": [["<expression>", ",", "<expression_list>"], ["<expression>"]], 
                        "<identifier>": [["<expression>", ",", "<expression_list>"], ["<expression>"]], "<integer>": [["<expression>", ",", "<expression_list>"], ["<expression>"]]}, 
                    "<manifest_tuple>": {"[": ["[", "<expression_list>", "]"]}, 
                    "<expression>": {"+": [["<basic_expression>"], ["<special_expression>"]], "-": [["<basic_expression>"], ["<special_expression>"]], "(": ["<basic_expression>"], 
                        "[": ["<special_expression>"], "<<": ["<special_expression>"], "if": ["<basic_expression>"], 
                        "ARRAY": ["<special_expression>"], "INTEGER": [["<basic_expression>"], ["<special_expression>"]], "not": ["<basic_expression>"], 
                        "<identifier>": [["<basic_expression>"], ["<special_expression>"]], "<integer>": [["<basic_expression>"], ["<special_expression>"]]}, 
                    "<basic_expression>": {"+": [["<equality>"], ["<operator_expression>"]], "-": [["<equality>"], ["<operator_expression>"]], "(": [["<parenthesized>"], ["<equality>"], ["<call>"], ["<bracket_expression>"], ["<operator_expression>"]],                        
                        "[": [["<equality>"], ["<operator_expression>"]], "if": [["<equality>"], ["<operator_expression>"], ["<conditional>"]],  "ARRAY":  [["<equality>"], ["<operator_expression>"]], "INTEGER":  [["<equality>"], ["<operator_expression>"]], 
                        "not": [["<equality>"], ["<operator_expression>"]], "<identifier>": [["<variable>"], ["<equality>"], ["<call>"], ["<bracket_expression>"], ["<operator_expression>"]], 
                        "<integer>": [["<equality>"], ["<operator_expression>"]]},
                    "<special_expression>": {"+": ["<manifest_constant>"], "-": ["<manifest_constant>"], "[": ["<manifest_tuple>"], "<<": ["<manifest_array>"], "ARRAY": [["<manifest_array>"], ["<manifest_constant>"]], 
                        "INTEGER": [["<manifest_array>"], ["<manifest_constant>"]], "<identifier>": [["<manifest_array>"], ["<manifest_constant>"]], "<integer>": ["<manifest_constant>"]},
                    "<bracket_expression>": {"(": ["<bracket_target>","[","<manifest_value_bracket>","]"], "<identifier>": ["<bracket_target>","[","<manifest_value_bracket>","]"]}, 
                    "<operator_expression>": {"+": [["<unary_expression>"], ["<binary_expression>"]], "-": [["<unary_expression>"], ["<binary_expression>"]], "(": ["<binary_expression>"], "[": ["<binary_expression>"], "if": ["<binary_expression>"], 
                        "not": [["<unary_expression>"], ["<binary_expression>"]], "<identifier>": ["<binary_expression>"]},
                    "<unary_expression>": {"+": ["<unary>", "<expression>"], "-": ["<unary>", "<expression>"], "not": ["<unary>", "<expression>"]},
                    "<binary_expression>": {"+": ["<expression>", "<binary>", "<expression>"], "-": ["<expression>", "<binary>", "<expression>"], "(": ["<expression>", "<binary>", "<expression>"], "[": ["<expression>", "<binary>", "<expression>"], 
                        "if": ["<expression>", "<binary>", "<expression>"], "not": [], "<identifier>": ["<expression>", "<binary>", "<expression>"]},
                    "<equality>": {"+": ["<expression>", "<comparison>", "<expression>"], "-": ["<expression>", "<comparison>", "<expression>"], "(": ["<expression>", "<comparison>", "<expression>"], "[": ["<expression>", "<comparison>", "<expression>"], 
                        "if": ["<expression>", "<comparison>", "<expression>"], "not": ["<expression>", "<comparison>", "<expression>"], "<identifier>": ["<expression>", "<comparison>", "<expression>"]}, 
                    "<actuals>": {"/=": [], "+": [], "-": [], "*": [], "/": [], "//": [], "^": [], ":=": [], "(": ["(", "<actuals_list>", ")"], ")": [], "[": [], "]": [], ",": [], "create": [], "from": [], "if": [], "not": [], "and": [], "or": [], "<identifier>": []}, 
                    "<actuals_list>": {"+": [["<expression>", ",", "<actuals_list>"], ["<expression>"]], "-": [["<expression>", ",", "<actuals_list>"], ["<expression>"]], "(": [["<expression>", ",", "<actuals_list>"], ["<expression>"]], 
                        "[": [["<expression>", ",", "<actuals_list>"], ["<expression>"]], "if": [["<expression>", ",", "<actuals_list>"], ["<expression>"]], "not": [["<expression>", ",", "<actuals_list>"], ["<expression>"]], "<identifier>": [["<expression>", ",", "<actuals_list>"], ["<expression>"]]},
                    "<creation_instruction>": {"feature": [], "create": ["create", "<manifest_type>", "<creation_call>"]},
                    "<creation_expression>": {"create": ["create", "<manifest_type>", "<explicit_creation_call>"], },
                    "<explicit_creation_call>": {"+": [], "-": [], ".": [".", "<unqualified_call>"], "(": [], "[": [], "feature": [], "create": [], "from": [], "if": [], "not": [], "<identifier>": []},
                    "<creation_call>": {"<identifier>": ["<variable>", "<explicit_creation_call>"]},
                    "<call>": {"<identifier>": [["<target>","<unqualified_call>"], ["<unqualified_call>"]]},
                    "<unqualified_call>": {"<identifier>": ["<feature_name>","<actuals>"]},
                    "<target>": {"(": ["<parenthesized>", "."], "<identifier>": [["<variable>", "."], ["<call>", "."]]},
                    "<bracket_target>": {"(": [["<call>"], ["<parenthesized>"]], "<identifier>": [["<call>"], ["<variable>"]]},
                    "<parenthesized>": {"(": ["(", "<expression>", ")"]},
                    "<variable>": {"<identifier>": ["<identifier>"]},
                    "<loop>": {"loop": ["<initialization>", "<exit_condition>", "<loop_body>", "end"], "from": ["<initialization>", "<exit_condition>", "<loop_body>", "end"], "until": ["<initialization>", "<exit_condition>", "<loop_body>", "end"]},
                    "<initialization>": {"loop": [], "from": ["from", "<compound>"], "until": []},
                    "<exit_condition>": {"loop": [], "until": ["until", "<equality>"]},
                    "<loop_body>": {"loop": ["loop", "<compound>"]},
                    "<conditional>": {"if": ["if", "<then_part>", "<else_part>", "end"]},
                    "<then_part>": {"+": ["<basic_expression>", "then", "<compound>"], "-": ["<basic_expression>", "then", "<compound>"], "(": ["<basic_expression>", "then", "<compound>"], "if": ["<basic_expression>", "then", "<compound>"], "not": ["<basic_expression>", "then", "<compound>"], "<identifier>": ["<basic_expression>", "then", "<compound>"]},
                    "<else_part>": {"end": [], "else": ["else", "<compound>"]},
                    "<binary>": {"<": ["<"], ">": [">"], "<=": ["<="], ">=": [">="], "+": ["+"], "-": ["-"], "*": ["*"], "/": ["/"], "//": ["//"], "^": ["^"], "and": ["and"], "or": ["or"]},
                    "<unary>": {"+": ["+"], "-": ["-"], "not": ["not"]},
                    "<comparison>": {"/=": ["/="], "=": ["="]},
                    "<sign>": {"+": ["+"], "-": ["-"], "<integer>": []}
                    }
productions_panic_table = {"<class_header>": ["end", "feature", "create"],
                            "<class_name>": ["end", "feature", "create"],
                            "<feature_name>": ["("],
                            "<entity_declaration_list>": [")"],
                            "<entity_declaration_group>": [","],
                            "<identifier_list>": [":"],
                            "<type_mark>": [",", ")"],
                            "<type>": ["]", ":="],
                            "<assigner_call>": [":=", "create", "loop", "from", "until"],
                            "<manifest_constant>": ["/=", "*", "/", "//", "^", ":=", ")", ",", "do", "and", "or"],
                            "<manifest_type>": ["."],
                            "<manifest_value>": ["/=", "*", "/", "//", "^", ":=", ")", ",", "do", "and", "or"],
                            "<manifest_array>": ["/=", "+", "-","*", "/", "//", "^", ":=", ")", ",", "and", "or"],
                            "<expression_list>": ["]", ">>"],
                            "<manifest_tuple>": ["/=", "+", "-","*", "/", "//", "^", ":=", ")", ",", "and", "or"],
                            "<target>": ["."]}
stack = [initial_non_terminal]
current_token_index = 0

# =========== ESTRUTURAS PARA A ÁRVORE DE DERIVAÇÃO =========================

@dataclass
class Node:
    type: string #NT ou T
    value: string

@dataclass
class Parent:
    parent_node: Node
    children: List[Node]

    def addNewChildren(self, new_children):
        for child in new_children:
            new_parent = Parent(Node("NT", child), [])
            self.children.append(new_parent)

       # print(self.children)

@dataclass
class DerivationTree:
    initial_node: Parent

    def __init__(self):
        self.initial_node = Parent(Node("NT", initial_non_terminal), [])
    


tokens = lexical_analyzer.main("code.txt")
derivation_tree = DerivationTree()

# =========== FUNÇÕES DA TABELA DE ANÁLISE =========================
def areListsIntersecctioned(terminals_list, following_tokens):
    for token in following_tokens:
        print(token.lexeme)
        if token.lexeme in terminals_list:
            return True
    return False

def conflictResolution(non_terminal, terminal, following_tokens): #VERIFICAR TODOS OS ISALNUM
    if non_terminal == "<identifier_list>":
       return 0 if following_tokens[0] == [","] else 1 #se tem , então <identifier> , <identifier_list> 
    elif non_terminal == "<instruction>":
        return 1 if areListsIntersecctioned([":="], following_tokens) else 0
    elif non_terminal == "<expression_list>":
       return 0 if areListsIntersecctioned([","], following_tokens) else 1 #ATENÇAÕ AQUI!!!
    elif non_terminal == "<expression>":
        if terminal in ["+", "-"]:
            return 1 if following_tokens[0].isdigit() else 0 #se for numero, só pode ser derivado por special_exp -> manifest_constant
        if terminal == "INTEGER" or terminal=="<identifier>": #ATENÇÃO: AQUI NAO É O PROXIMO TERMINAL, NECESSARIAMENTE, MAS EM UM DOS PROXIMOS
            return 0 if areListsIntersecctioned( ["<", ">",">=", "<=", "+", "-", "*", "/", "//", "^", "and", "or"], following_tokens) else 1
    elif non_terminal == "<basic_expression>":
        if (terminal in ["+", "-", "[", "ARRAY", "INTEGER", "not"]) or (terminal.isdigit()):
            return 0 if areListsIntersecctioned(["<", ">",">=", "<="], following_tokens)  else 1
        elif terminal in ["("]:
            if areListsIntersecctioned(["<", ">",">=", "<="], following_tokens):
                return 1
            elif areListsIntersecctioned(["."], following_tokens):
                return 2
            elif areListsIntersecctioned(["["], following_tokens):
                return 3
            elif areListsIntersecctioned(["+", "-", "*", "/", "//", "^", "and", "or"], following_tokens):
                return 4
            else: 
                return 0
        elif terminal in ["if"]:
            if areListsIntersecctioned(["<", ">",">=", "<="], following_tokens):
                return 0
            elif areListsIntersecctioned(["+", "-", "*", "/", "//", "^", "and", "or"], following_tokens):
                return 1
            else:
                return 2
        elif terminal == "<identifier>":
            if areListsIntersecctioned(["<", ">",">=", "<="], following_tokens):
                return 1
            elif areListsIntersecctioned(["."], following_tokens):
                return 2
            elif  areListsIntersecctioned(["["], following_tokens):
                return 3
            elif  areListsIntersecctioned(["+", "-", "*", "/", "//", "^", "and", "or"], following_tokens):
                return 4
            else: 
                return 0    
    elif non_terminal == "<special_expression>":
        if (terminal in ["ARRAY", "INTEGER"]) or (terminal == "<identifier>"):
            return 0 if areListsIntersecctioned(["<<"], following_tokens) else 1  
    elif non_terminal == "<operator_expression>":
        if terminal in ["+", "-", "not"]:
            return 1 if areListsIntersecctioned(["+", "-", "*", "/", "//", "^", "and", "or"], following_tokens) else 0                
    elif non_terminal == "<actuals_list>":
        return 0 if  areListsIntersecctioned([","], following_tokens) else 1
    elif non_terminal == "<call>":
        return 0 if  areListsIntersecctioned(["."], following_tokens) else 1
    elif non_terminal == "<target>":
        return 1 if areListsIntersecctioned(["."], following_tokens) else 0 #nesse caso aqui, é se tiver OUTRO ponto depois do primeiro
    elif non_terminal == "<bracket_target>":
        if terminal == "(":
            return 0 if areListsIntersecctioned(["."], following_tokens) else 1
        elif terminal == "<identifier>":
            return 1 if areListsIntersecctioned([".", "("], following_tokens) else 0


# =========== FUNÇÕES DE PILHA =====================

def push(lista):
    # colocar na ordem inversa
    listReversed = lista.copy()
    listReversed.reverse()
    
    for item in listReversed:
        stack.append(item)
    print(stack)

def pop():
    temporary = stack[-1]
    del stack[-1]
    return temporary

def getTopStack():
    return(stack[len(stack) - 1])


# =========== FUNÇÕES GERAIS =====================
def getFollowingTokens():
    following_tokens = tokens[slice(current_token_index+1, current_token_index+6)]
    print(following_tokens)
    return following_tokens

def recursiveParser(current_parent_node):
    print(f"chamada para o nó {current_parent_node.parent_node.value}")
    global current_token_index

    current_token = tokens[current_token_index]
    print(f"topo da pilha: {getTopStack()} topo da fita: {current_token.lexeme}")

    if current_token.lexeme_class == 'id':
        terminal = "<identifier>"
    elif current_token.lexeme_class == 'int':
        terminal = "<integer>"
    else:
        terminal = current_token.lexeme

    #se for comentario, nada acontece
    if current_token.lexeme_class == 'comment':
        current_token_index += 1
        recursiveParser(current_parent_node)
    #se topo_pilha e current_token forem iguais, desempilha e reconhece
    elif terminal == getTopStack():      
        print("entrei")  
        pop()                   
        current_parent_node.addNewChildren([current_token.lexeme])
        current_token_index += 1
    #procura a transição
    else:
        try:
            children_list = productions_table[getTopStack()][terminal]
            print(len(children_list))


            if (len(children_list) > 1) and (type(children_list[0]) == list):
                children_index = conflictResolution(getTopStack(), terminal, getFollowingTokens())
                print(children_index)

                pop()
                push(children_list[children_index])
                current_parent_node.addNewChildren(children_list[children_index])
            else:               
                pop()
                push(children_list)            
                current_parent_node.addNewChildren(children_list)

            for child in current_parent_node.children:
                recursiveParser(child)
                

        except: #Não existe a produção
            print("não existe transição")
            exit()
    

def main():
    current_parent_node = derivation_tree.initial_node 
    recursiveParser(current_parent_node)     
        

main()

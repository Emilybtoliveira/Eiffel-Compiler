import read_source_code

###### PRÉ ANÁLISE LEXICA
tokens_dict = {} # adicionar aqui os tokens que vao ser do tipo ["lexema" : "classe"].

reserved_words = ["feature", "none", "assign", "current", "create", "loop", "from", "until", "all", "some", "integer", "array"]
delimiters = ["(", ")", "{", "}", "[", "]", ";", ",", "<<", ">>", "do", "end"]
operators = ["=", "/=", "<", ">", "<=", ">=", "+", "-", "not", "*", "/", "//", "^", "and", "or", ":=", "assign", ":", "."]

##### FUNÇÕES BÁSICAS
def addNewToken(lexeme, lexeme_class):
    for key in tokens_dict.keys(): #verifica se já existe o token no dicionario
        if key == lexeme:
            return
        
    tokens_dict[lexeme] = lexeme_class
    print(tokens_dict)

def throwError(error_position, error_message):
    print(f'An error has be found in position {error_position}.\nSee description: {error_message}')


##### LOOP PRINCIPAL
def main():
    source_code = read_source_code.generateCodeString()    

    #ordem de chamada dos reconhecedores
    commentsRecognizer()
    delimitersRecognizer()
    operatorsRecognizer()
    idRecognizer() #aqui verifica-se se é uma palavra reservada
    constantRecognizer()

    

if __name__ == '__main__': 
    main() 
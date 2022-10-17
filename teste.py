from dataclasses import dataclass


from dataclasses import dataclass
import string

from attr import field

@dataclass(order=True)
class Token:
    lexeme: string
    lexeme_class: string

    def __post__init__(self):
        self.sort_index = self.ordemTkn


texto = "open(who:PERSON,sla:ALGO)"
newString = texto
listaLex = [Token(lexeme=':', lexeme_class='opr'),
Token(lexeme='(', lexeme_class='del'),
Token(lexeme='open', lexeme_class='id'),
Token(lexeme='who', lexeme_class='id'),
Token(lexeme=':', lexeme_class='opr'),
Token(lexeme=',', lexeme_class='del'),
Token(lexeme='PERSON', lexeme_class='id'),
Token(lexeme='sla', lexeme_class='id'),
Token(lexeme=')', lexeme_class='del'),
Token(lexeme='ALGO', lexeme_class='id')
]

def ordenacaoTokens(source,listaQnt):


    lista = [x.lexeme for x in listaLex]

# posicoes vao ser iguais
# listaLex[0].lexeme_class = "teste" isso eh possivel!


    newList = [0 for x in range(len(lista))]
    ordem = 0
    qntRem = 0
    word = ""
    contador = 0
    while len(texto)!=contador:
        char = texto[contador]
        word+=char
        if word.replace(" ","") in lista:
            word = word.replace(" ","")
            if word in [">"]:
                # checar aqui apra os operadores compostos
                if texto[contador+1]==">":
                    word+=">"
                    contador+=1
            indexn = lista.index(word)+qntRem
            print(f"palavra: {word}, ordem = {ordem}, index = {indexn}")
            
            listaLex[indexn].ordemTkn = ordem
            newList[ordem] = word
            if lista.count(word)>1:
                del lista[indexn]
                qntRem+=1
            
            print(lista)
            ordem+=1
            word = ""
            contador+=1
        else:
            contador+=1


def teste(e):
    return e.ordemTkn
listaLex.sort(key=teste)

for x in listaLex:
    print(x)



    
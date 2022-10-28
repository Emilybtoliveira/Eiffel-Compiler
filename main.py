import lexical_analyzer, syntax_analyzer
import argparse

def main():
    tokens = lexical_analyzer.main()
    syntax_analyzer.main(tokens)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='            Analisador Léxico de BNF Resumida\n'
        + '    Apresentado a Profa. Roberta Vilhena em 19/09/2022\n'
        + '        Disciplina 2022.1 - COMP379 - COMPILADORES\n'
        + '                     Linguagem Eiffel\n\n'
        + '    Por: Emily B. T. Oliveira, \n'
        + '         Felipe F. Vasconcelos, \n'
        + '         Taígo I. M. Pedrosa\n',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-i', '--input', metavar='INPUT', dest='input',
                        help='Sets the input file\'s path.\n'
                        + 'If input isn\'t set, it will be requested interactively.')
    parser.add_argument('--unit-testing', dest='test', action='store_true',
                        help='Runs unit tests and returns.\n')
    args = parser.parse_args()

    main()
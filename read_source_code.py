def generateCodeString():
    source = open("code.txt", "r")

    #print(source.readline(1))
    source_code = source.read()
    #print(source_code)

    """  for i in range (0, len(source_code)):
        print(source_code[i])

        if source_code[i] == '?':
            var = i

    print(var)
    print(ord(source_code[var]))  #unicode da letra """

    source.close()

    return source_code
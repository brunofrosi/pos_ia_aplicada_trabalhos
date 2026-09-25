def separar_equacao(equacao):
    equacao = equacao.replace(" ", "")

    while "(" in equacao:
        inicio = equacao.rfind("(") #procura do fim pro começo
        fim = equacao.find(")", inicio) # procura do começo pro fim. por causa do parametro "inicio", ele procura do "(" em diante

        if fim == -1:
            raise ValueError("Parenteses de fechamento inexistente ou mal colocado")

        sub_expressao = equacao[inicio + 1 : fim]

        resultado_sub = separar_equacao(sub_expressao) [0]

        equacao = equacao[:inicio] + str(resultado_sub) + equacao[fim + 1:]
    
    numero = ""
    numeros = []
    operadores = []

    for caracter in equacao:
        if caracter.isdigit() or caracter == ".":
            numero += caracter

        elif caracter in "+-*/":
            if numero:
                numeros.append(float(numero))
                numero = ""

            operadores.append(caracter)

    if numero:
        numeros.append(float(numero))

    i = 0

    while i < len(operadores):
        if operadores[i] in "*/":
            x = operadores.pop(i)

            n1 = numeros.pop(i)
            n2 = numeros.pop(i)

            if x == "*":
                r = n1 * n2

            else:
                r = n1 / n2 if n2 != 0 else 0

            numeros.insert(i, r)
        else:
            i += 1


    i = 0
    while i < len(operadores):
        if operadores[i] in "+-":
            x = operadores.pop(i)

            n1 = numeros.pop(i)
            n2 = numeros.pop(i)

            if x == "+":
                r = n1 + n2

            else:
                r = n1-n2
            numeros.insert(i, r)
        else:
            i+=1
        

    return numeros


print(separar_equacao(equacao=input("Digite uma equação: ")))

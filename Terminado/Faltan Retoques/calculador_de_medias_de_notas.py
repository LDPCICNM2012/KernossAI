#Calculador de medias de notas
#AVISO. Para que este codigo funcione, necesitas tener Ollama con el modelo "qwen2.5-coder:3b" instalado. Aparte, necesitarás un mac por los applescript. Lo siento, ya haré un port para windows.

import time
notas = [] #Lista donde se guardan las notas que pongas
nombres_notas = [] #Lista donde se guardan los nombres de las notas con sus respectivas notas(hablando elegantemente :)

print("Bienvenido al calculador de notas") #Buena bienvenida señores
numero_notas = int(input("Cuantas notas quieres calcular: ")) #Le pregunta al usuario que cantidad cantosa de notas quiere calcular


def calcular_media(lista): #Funcion para calcular la media de la lista
    if not lista: #Si está vacio (que no va a estar) que de 0 para que no de errores de tonto
        return 0
    return sum(lista) / len(lista) #Suma todas las notas de la lista y las divida por el nuevo ellas.


for i in range(numero_notas): #Por cada nota dicha en la pregumnta:
    pregunta = input("¿Tu nota tiene subnotas? (si/no): ").lower() #Pregunta si hay subnotas en la nota
    nombre_nota = input("Ingresa el nombre de la nota principal: ")#Pregunta el nombre de la nota principal
    nombres_notas.append(nombre_nota) #Mete el nombre de la nota principal en la lista de las notas

    if pregunta == "si": #Si la pregunta de si hay subnotas es correctamente y verdadermente afirmativa:
        subnotas = [] #Lista de subnotas
        nombres_subnotas = [] #Lista de nombres de subnotas

        cantidad = int(input("¿Cuantas subnotas tiene?: ")) #No hace falta especificar pero pregunta cuantas subnotas tiene

        for j in range(cantidad): #Se pone j pq había que poner una letra como arriba que esta i pero para no utilizar la misma.
            nombre_sub = input(f"Nombre de la subnota {j + 1}: ") #Pregunta el nombre de la subnota
            valor_sub = float(input(f"Nota de {nombre_sub}: ")) #Pregunta la nota de la subnota

            nombres_subnotas.append(nombre_sub) #Mete el nombre de la subnota en la lista de nombres de subnotas
            subnotas.append(valor_sub)#Mete la nota de la subnota en la lista de subnotas

        nota_final = calcular_media(subnotas) #Calcula la media de las subnotas

        print(f"\nSubnotas de {nombre_nota}:") #Como he aporendido de otros proyectos, \n es para que haya un salto de linea y quede mas clean.
        for nombre, valor in zip(nombres_subnotas, subnotas): #Zip es para juntar dos listas, la de las subnotas y la de sus nombres(no me juzguen, he tenido que aprender esto yo solo)
            print(f" - {nombre}: {valor}") #Ponemos diseño con el -(pq puedo) y damos los valores

        print(f"Nota final de {nombre_nota}: {nota_final}\n") #Fuera ya del bloque de las subnotas, calcula la nota final ya de todo

    else:
        nota_final = float(input("Ingresa la nota: ")) #Si no hay subnotas, pregunta directamente la nota de la nota principal y la mete en nota final para que se guarde en la lista de notas.

    notas.append(nota_final) #Mete la nota en la lista de notas

# Mostrar resultados
for i, (nombre, nota) in enumerate(zip(nombres_notas, notas), start=1): #Esto es lo de antes basicamente, por cada nota y nombre en las 2 listas:
    print(f"Nota {i}: {nota}, Nombre: {nombre}") #Imprime la nota con su nombre
    time.sleep(1)#Pausa 100% necesaria

print(f"\nLa media total es: {calcular_media(notas)}") #Media final x fin. 
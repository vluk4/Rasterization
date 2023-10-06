import sys
from tkinter import Tk, Label, Entry, Button, Text, Scrollbar, END

import matplotlib.pyplot as plt
import numpy as np

# Exemplos:
# Triângulos equiláteros:
# -0.9, -0.25; -0.5,-0.25; -0.7, 0.25
# -0.25,0; 0.25,0; 0,0.433

# Quadrados:
#  -0.25,-0.25; 0.25,-0.25; 0.25,0.25; -0.25,0.25
# -0.5,-0.5; 0.5,-0.5; 0.5,0.5; -0.5,0.5

# Hexágonos:
# -0.5,0; -0.25,0.433; 0.25,0.433; 0.5,0; 0.25,-0.433; -0.25,-0.433
# -0.25,0.125; -0.125,0.375; 0.125,0.375; 0.25,0.125; 0.125,-0.125; -0.125,-0.125

# Retas:
# -1,0;1,0
# 0,-1;0,1
# -1,-1;1,1
# -1,1;1,-1
# 0.75,0.5;-0.75,-1
# Lista de poligonos
poligonos = []


def normalizar_coordenadas(pontos, res_x, res_y):
    pontos_normalizados = []
    for ponto in pontos:
        # Transforma a coordenada x e y no intervalo [-1, 1] para o espaço de pixel
        x = (ponto[0] + 1) / 2 * res_x
        y = (ponto[1] + 1) / 2 * res_y
        pontos_normalizados.append((x, y))
    return pontos_normalizados


def rasterizar_reta(x1, y1, x2, y2, res_x, res_y):
    # Inicializa uma matriz vazia com a resolução especificada
    imagem = np.zeros((res_y, res_x))

    # Calcula as diferenças entre as coordenadas x e y dos pontos
    dx = x2 - x1
    dy = y2 - y1

    m = dy / dx if dx != 0 else 0
    b = y2 - m * x2 if dx != 0 else 0

    # Verifica se a reta é mais horizontal do que vertical
    if abs(dx) > abs(dy):
        if x1 > x2:
            x1, x2, y1, y2 = x2, x1, y2, y1
        x, y = x1, y1
        # Varre a reta no sentido horizontal
        while x < x2:
            if 0 <= x < res_x and 0 <= int(y) < res_y:
                imagem[int(y), int(x)] = 1
            x += 1
            y = m * x + b

    # Caso a reta seja mais vertical do que horizontal
    else:
        if y1 > y2:
            x1, x2, y1, y2 = x2, x1, y2, y1
        x, y = x1, y1
        # Varre a reta no sentido vertical
        while y < y2:
            if 0 <= x < res_x and 0 <= int(y) < res_y:
                imagem[int(y), int(x)] = 1
            y += 1
            x = (y - b) / m

    return imagem


def rasteriza_poligno(imagem):
    res_y, res_x = imagem.shape
    pontos_internos = []
    # Iterar sobre cada pixel na imagem
    for y in range(res_y):
        count = 0
        ponto_aux = []
        for x in range(res_x):
            if imagem[y, x] == 1:
                if y < res_y and (x + 1) < res_x and imagem[y, x + 1] == 1:
                    pass
                else:
                    count += 1

            if 0 < count and count % 2 == 1:
                ponto_aux.append([y, x])
        if len(ponto_aux) != 0 and count % 2 == 0:
            pontos_internos.append(ponto_aux)

    for ponto in pontos_internos:
        for p in ponto:
            imagem[p[0], p[1]] = 1

    return imagem


def adicionar_poligono():
    pontos_str = entrada_pontos.get()
    entrada_pontos.delete(0, END)
    poligonos_str = pontos_str.split(';')
    poligonos.append(poligonos_str)
    texto_poligonos.insert("end", f"{len(poligonos)}. {pontos_str}\n")


def mostrar_poligonos():
    res_x, res_y = map(int, entrada_resolucao.get().split('x'))
    imagem_final = np.zeros((res_y, res_x))

    for poligono in poligonos:
        poligono_rasterizado = np.zeros((res_y, res_x))
        pontos = [tuple(map(float, ponto.split(','))) for ponto in poligono]
        pontos_normalizados = normalizar_coordenadas(pontos, res_x, res_y)
        for i, ponto1 in enumerate(pontos_normalizados):
            ponto2 = pontos_normalizados[i - 1]  # O ponto anterior na lista
            reta_rasterizada = rasterizar_reta(ponto1[0], ponto1[1], ponto2[0], ponto2[1], res_x, res_y)
            poligono_rasterizado = np.maximum(poligono_rasterizado, reta_rasterizada)

        imagem_reasterizada_poligonos = rasteriza_poligno(poligono_rasterizado)
        imagem_final = np.maximum(imagem_final, imagem_reasterizada_poligonos)

    plt.title(f'Resolução: {res_x}x{res_y}')
    plt.imshow(imagem_final, cmap='gray', origin='lower')
    plt.xticks(range(0, res_x, res_x // 10))
    plt.yticks(range(0, res_y, res_y // 10))
    plt.show()


root = Tk()
root.title("Rasterização de Polígonos")

Label(root, text="Pontos do Polígono (x1,y1;x2,y2;...):").grid(row=0, column=0, sticky="w")
entrada_pontos = Entry(root, width=30)
entrada_pontos.grid(row=0, column=1)

botao_adicionar = Button(root, text="Adicionar Polígono", command=adicionar_poligono)
botao_adicionar.grid(row=1, column=0, columnspan=2)

Label(root, text="Polígonos adicionados:").grid(row=2, column=0, sticky="w")
texto_poligonos = Text(root, width=35, height=10)
texto_poligonos.grid(row=3, column=0, columnspan=2)

scrollbar = Scrollbar(root, command=texto_poligonos.yview)
scrollbar.grid(row=3, column=2, sticky="ns")
texto_poligonos.config(yscrollcommand=scrollbar.set)

Label(root, text="Resolução (largura x altura):").grid(row=4, column=0, sticky="w")
entrada_resolucao = Entry(root, width=30)
entrada_resolucao.grid(row=4, column=1)

botao_rasterizar = Button(root, text="Rasterizar Polígonos", command=mostrar_poligonos)
botao_rasterizar.grid(row=5, column=0, columnspan=2)

root.mainloop()

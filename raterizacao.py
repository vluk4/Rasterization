import sys
from tkinter import Tk, Label, Entry, Button, Text, Scrollbar, END
import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np

# Exemplos:
# Triângulos equiláteros:
# -0.9, -0.25; -0.5,-0.25; -0.7, 0.25
# Quadrado:
# 0.5,0; 0.9,0; 0.9,0.4; 0.5,0.4
# Hexágono:
# -0.25,0.125; -0.125,0.375; 0.125,0.375; 0.25,0.125; 0.125,-0.125; -0.125,-0.125
# Retas:
# -1,0;1,0
# 0,-1;0,1
# -1,-1;1,1
# -1,1;1,-1
# 0.75,0.5;-0.75,-1
# Curvas
# -0.5, 0.5; -0.2, 0.5; 0, 0.2; 0, -0.2; 5
# 0.2, -0.2; 0.5, -0.5; 0.2, 0; -0.2, 0; 5

poligonos = []
curvas_hermite = []


def normalizar_coordenadas(pontos, res_x, res_y):
    pontos_normalizados = []
    for ponto in pontos:
        # Transforma a coordenada x e y no intervalo [-1, 1] para o espaço de pixel
        x = (ponto[0] + 1) / 2 * res_x - 1
        y = (ponto[1] + 1) / 2 * res_y - 1
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
        while x <= x2:
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
        while y <= y2:
            if 0 <= x < res_x and 0 <= int(y) < res_y:
                imagem[int(y), int(x)] = 1
            y += 1
            if m != 0:
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


def rasterizar_curva_hermite(p1, p2, t1, t2, res_x, res_y, num_points):
    imagem = np.zeros((res_y, res_x))
    points = []

    # c(t) = (2t^3 - 3t^2 + 1)P1 + (t^3 - 2t^2 + t)T1 + (-2t^3 + 3t^2)P2 + (t^3 - t^2)T2
    for t in range(num_points):
        t_normalized = t / (num_points - 1)
        h1 = 2 * t_normalized ** 3 - 3 * t_normalized ** 2 + 1
        h2 = -2 * t_normalized ** 3 + 3 * t_normalized ** 2
        h3 = t_normalized ** 3 - 2 * t_normalized ** 2 + t_normalized
        h4 = t_normalized ** 3 - t_normalized ** 2
        x = h1 * p1[0] + h2 * p2[0] + h3 * t1[0] + h4 * t2[0]
        y = h1 * p1[1] + h2 * p2[1] + h3 * t1[1] + h4 * t2[1]
        points.append((int(x), int(y)))

    # Rasteriza retas
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        imagem = np.maximum(imagem, rasterizar_reta(x1, y1, x2, y2, res_x, res_y))
    return imagem


def adicionar_poligono():
    pontos_str = entrada_pontos.get()
    entrada_pontos.delete(0, END)
    poligonos_str = pontos_str.split(';')
    poligonos.append(poligonos_str)
    texto_pontos.insert("end", f"{len(poligonos)}. {pontos_str}\n")


def adicionar_curva_hermite():
    pontos_str = entrada_curva_hermite.get()
    entrada_curva_hermite.delete(0, END)
    curva_hermite_str = pontos_str.split(';')
    curvas_hermite.append(curva_hermite_str)
    texto_pontos.insert("end", f"{len(curvas_hermite)}. {pontos_str}\n")


def mostrar_poligonos():
    todas_resolucoes = entrada_resolucao.get().split(';')
    todas_imagens = []
    for index,resolucao in enumerate(todas_resolucoes):
        res_x,res_y = map(int,resolucao.split('x'))
    # res_x, res_y = map(int, entrada_resolucao.get().split('x'))
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


        for curva_hermite in curvas_hermite:
            pontos = [tuple(map(float, ponto.split(','))) for ponto in curva_hermite[:-1]]
            pontos_normalizados = normalizar_coordenadas(pontos, res_x, res_y)
            p1 = pontos_normalizados[0]
            p2 = pontos_normalizados[1]
            t1 = pontos_normalizados[2]
            t2 = pontos_normalizados[3]
            pontos_qnt = curva_hermite[-1]
            curva_hermite_rasterizada = rasterizar_curva_hermite(p1, p2, t1, t2, res_x, res_y, int(pontos_qnt))
            imagem_final = np.maximum(imagem_final, curva_hermite_rasterizada)
        todas_imagens.append(imagem_final)
    plt.figure(figsize=(10,10))

    for index,resolucao in enumerate(todas_resolucoes):
        # for imageIndex,image in enumerate(todas_imagens):
        res_x, res_y = map(int, todas_resolucoes[index].split('x'))
        plt.subplot(2, 2, index+1)
        plt.imshow(todas_imagens[index],cmap='gray',origin='lower')
        plt.title(f'Resolução: {res_x}x{res_y}')
        plt.xticks(range(0, res_x, res_x // 10))
        plt.yticks(range(0, res_y, res_y // 10))
    plt.show()


root = Tk()
root.title("Rasterização")

# Retas e polígonos
Label(root, text="Pontos da reta ou polígono (x1,y1;x2,y2;...):").grid(row=0, column=0, sticky="w", pady=10)
entrada_pontos = Entry(root)
entrada_pontos.grid(row=0, column=1, sticky=tk.W + tk.E)

botao_adicionar = Button(root, text="Adicionar Pontos", command=adicionar_poligono)
botao_adicionar.grid(row=1, column=0, columnspan=2, ipady=5)

Label(root, text="Curva de Hermite (P1x,P1y;p2x,p2y;T1x,T1y;T2x,T2y;qnt):").grid(row=2, column=0, sticky="w", pady=10)
entrada_curva_hermite = Entry(root, width=40)
entrada_curva_hermite.grid(row=2, column=1)

botao_adicionar = Button(root, text="Adicionar Pontos", command=adicionar_curva_hermite)
botao_adicionar.grid(row=3, column=0, columnspan=2, ipady=5)

Label(root, text="Pontos adicionados:").grid(row=4, column=0, sticky="w")
texto_pontos = Text(root, width=35, height=10)
texto_pontos.grid(row=4, column=0, columnspan=2, pady=10)

scrollbar = Scrollbar(root, command=texto_pontos.yview)
scrollbar.grid(row=4, column=3, sticky="ns")
texto_pontos.config(yscrollcommand=scrollbar.set)

Label(root, text="Resolução (largura x altura):").grid(row=6, column=0, sticky="w")
entrada_resolucao = Entry(root, width=30)
entrada_resolucao.grid(row=6, column=1, sticky=tk.W + tk.E)

botao_rasterizar = Button(root, text="Rasterizar", command=mostrar_poligonos)
botao_rasterizar.grid(row=7, column=0, columnspan=2, ipady=5, pady=10)

root.mainloop()

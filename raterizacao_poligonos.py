import sys
from tkinter import Tk, Label, Entry, Button, Text, Scrollbar, END

import matplotlib.pyplot as plt
import numpy as np

# Exemplos:
# Triângulos equiláteros:
# -0.9,-0.9; 0.9,-0.9; 0,0.9
# -0.25,0; 0.25,0; 0,0.433

# Quadrados:
# -0.8,-0.8; 0.8,-0.8; 0.8,0.8; -0.8,0.8
# -0.5,-0.5; 0.5,-0.5; 0.5,0.5; -0.5,0.5

# Hexágonos:
# -0.5,0; -0.25,0.433; 0.25,0.433; 0.5,0; 0.25,-0.433; -0.25,-0.433
# -0.25,0.125; -0.125,0.375; 0.125,0.375; 0.25,0.125; 0.125,-0.125; -0.125,-0.125

# Lista de poligonos
poligonos = []


def normalizar_coordenadas(pontos, res_x, res_y):
    pontos_normalizados = []
    for ponto in pontos:
        # Transforma a coordenada x e y no intervalo [-1, 1] para o espaço de pixel
        x = (ponto[0] + 1) / 2 * (res_x - 1)
        y = (ponto[1] + 1) / 2 * (res_y - 1)
        pontos_normalizados.append((x, y))
    return pontos_normalizados


def rasterizar_poligono(pontos, res_x, res_y):
    imagem = np.zeros((res_y, res_x))
    np.set_printoptions(threshold=sys.maxsize, linewidth=sys.maxsize)

    # Itera através de todas as linhas horizontais da imagem (scanlines)
    for y in range(res_y):
        intersecoes = []

        # Itera através das arestas do polígono
        for i, ponto1 in enumerate(pontos):
            ponto2 = pontos[i - 1]  # O ponto anterior na lista

            # Verifica se a scanline cruza a aresta
            if (ponto1[1] <= y < ponto2[1]) or (ponto2[1] <= y < ponto1[1]):
                # Calcular a coordenada x da interseção
                x = ((y - ponto1[1]) * (ponto2[0] - ponto1[0]) / (ponto2[1] - ponto1[1])) + ponto1[0]
                intersecoes.append(x)

        # Ordena as interseções pela coordenada x
        intersecoes.sort()

        # Preenche os pixels entre cada par de interseções
        for i in range(0, len(intersecoes) - 1, 2):
            x_start, x_end = int(intersecoes[i]), int(intersecoes[i + 1])
            imagem[y, x_start:x_end] = 1

    # Mostra o modelo no espaço continuo
    print(np.array_str(imagem))
    return imagem


def adicionar_poligono():
    pontos_str = entrada_pontos.get()
    entrada_pontos.delete(0, END)
    pontos = [tuple(map(float, ponto.split(','))) for ponto in pontos_str.split(';')]
    poligonos.append(pontos)
    texto_poligonos.insert("end", f"{len(poligonos)}. {pontos_str}\n")


def blend_rgba(bg, fg):
    alpha_bg = 1 - fg[:, :, 3]
    out_alpha = fg[:, :, 3] + bg[:, :, 3] * alpha_bg
    out_alpha[out_alpha == 0] = 1

    out = np.zeros_like(bg)
    for i in range(3):
        out[:, :, i] = (fg[:, :, i] * fg[:, :, 3] + bg[:, :, i] * bg[:, :, 3] * alpha_bg) / out_alpha

    out[:, :, 3] = out_alpha
    return out


def mostrar_poligonos():
    res_x, res_y = map(int, entrada_resolucao.get().split('x'))
    imagem_final = np.zeros((res_y, res_x, 4))

    for pontos in poligonos:
        pontos_normalizados = normalizar_coordenadas(pontos, res_x, res_y)
        imagem_poligono = rasterizar_poligono(pontos_normalizados, res_x, res_y)

        cor = np.random.rand(3)  # Gerar cor aleatória
        transparencia = np.random.uniform(0.3, 4)  # Gerar transparência aleatória

        # Criar imagem RGBA para o polígono atual
        imagem_rgba = np.zeros((res_y, res_x, 4))
        for i in range(3):
            imagem_rgba[:, :, i] = np.where(imagem_poligono == 1, cor[i], 0)
        imagem_rgba[:, :, 3] = np.where(imagem_poligono == 1, transparencia, 0)

        # Combinar imagem_rgba com imagem_final usando blend_rgba
        imagem_final = blend_rgba(imagem_final, imagem_rgba)

    plt.title(f'Resolução: {res_x}x{res_y}')
    plt.imshow(imagem_final, origin='upper')
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

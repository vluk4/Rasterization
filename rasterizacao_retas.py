import sys

import numpy as np
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import messagebox


def normalizar_coordenadas(x1, y1, x2, y2, res_x, res_y):
    x1 = (x1 + 1) * res_x / 2
    x2 = (x2 + 1) * res_x / 2
    y1 = (y1 + 1) * res_y / 2
    y2 = (y2 + 1) * res_y / 2
    return x1, y1, x2, y2


def rasterizar_reta(x1, y1, x2, y2, res_x, res_y):
    # Inicializa uma matriz vazia com a resolução especificada
    imagem = np.zeros((res_y, res_x))

    # Calcula as diferenças entre as coordenadas x e y dos pontos
    dx = x2 - x1
    dy = y2 - y1

    # Verifica se a reta é mais horizontal do que vertical
    if abs(dx) > abs(dy):
        if x1 > x2:
            x1, x2, y1, y2 = x2, x1, y2, y1
        m = dy / dx
        b = y1 - m * x1
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
        m = dx / dy
        b = x1 - m * y1
        x, y = x1, y1

        # Varre a reta no sentido vertical
        while y < y2:
            if 0 <= x < res_x and 0 <= int(y) < res_y:
                imagem[int(y), int(x)] = 1
            y += 1
            x = m * y + b

    return imagem


def processar_entrada():
    try:
        np.set_printoptions(threshold=sys.maxsize, linewidth=sys.maxsize)

        semirretas_str = entrada_semirretas.get().strip()
        semirretas = [tuple(map(float, semirreta.split(','))) for semirreta in semirretas_str.split(';')]

        resolucao_str = entrada_resolucao.get().strip()
        resolucao = tuple(map(int, resolucao_str.split(',')))

        imagem = np.zeros((resolucao[1], resolucao[0]))

        for semirreta in semirretas:
            x1, y1, x2, y2 = normalizar_coordenadas(*semirreta, resolucao[0], resolucao[1])
            imagem_rasterizada = rasterizar_reta(x1, y1, x2, y2, resolucao[0], resolucao[1])
            imagem = np.maximum(imagem, imagem_rasterizada)

        # Atualiza o widget Text com a matriz da imagem
        matriz_text.delete(1.0, END)
        matriz_text.insert(INSERT, np.array_str(imagem))

        plt.imshow(imagem, cmap='gray', origin='lower')
        plt.title(f'Resolução: {resolucao[0]}x{resolucao[1]}')
        plt.show()

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao processar a entrada: {str(e)}")


# Cria a janela principal da aplicação
janela = Tk()
janela.title("Rasterização de Semirretas")

# Widgets de entrada para as semirretas e resolução
Label(janela, text="Semirretas (x1,y1,x2,y2);(x1,y1,x2,y2):").grid(row=0, column=0, sticky=W)
entrada_semirretas = Entry(janela, width=50)
entrada_semirretas.grid(row=0, column=1, sticky=W, padx=(0, 20))

Label(janela, text="Resolução (x,y):").grid(row=1, column=0, sticky=W)
entrada_resolucao = Entry(janela, width=50)
entrada_resolucao.grid(row=1, column=1, sticky=W, padx=(0, 20))

botao_processar = Button(janela, text="Processar", command=processar_entrada)
botao_processar.grid(row=2, columnspan=2)


Label(janela, text="Matriz da imagem:").grid(row=3, column=0, sticky=W)
frame_text = Frame(janela)
frame_text.grid(row=4, columnspan=2)

matriz_text = Text(frame_text, width=120, height=30, wrap=NONE)
matriz_text.pack(side=LEFT, fill=Y)

scrollbar_y = Scrollbar(frame_text, orient=VERTICAL, command=matriz_text.yview)
scrollbar_y.pack(side=RIGHT, fill=Y)
matriz_text.config(yscrollcommand=scrollbar_y.set)

scrollbar_x = Scrollbar(frame_text, orient=HORIZONTAL, command=matriz_text.xview)
scrollbar_x.pack(side=BOTTOM, fill=X)
matriz_text.config(xscrollcommand=scrollbar_x.set)

janela.geometry("900x700")
janela.mainloop()

# -1,0,1,0; 0,-1,0,1; -1,-1,1,1; -1,1,1,-1

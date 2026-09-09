from collections import deque
import streamlit as st

def _parse_labirinto(labirinto_str):
    return [list(row) for row in labirinto_str.strip().split('\n')]

def procura_E_D(grid):
    E = None
    D = None
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == 'E':
                E = (r, c)
            elif grid[r][c] == 'D':
                D = (r, c)
    if not E:
        raise ValueError("Entrada E não encontrada.")
    if not D:
        raise ValueError("Destino D não encontrado.")
    return E, D

def _vizinhos(grid, l, c):
    vizinhos = []
    linhas, cols = len(grid), len(grid[0])
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)] 

    for dl, dc in directions:
        nl, nc = l + dl, c + dc
        if 0 <= nl < linhas and 0 <= nc < cols and grid[nl][nc] != '#':
            vizinhos.append((nl, nc))
    return vizinhos

def _reconstruir_caminho(caminho_i_dict, caminho_v_dict, meio_caminho):
    caminho_i = []
    current = meio_caminho
    while current is not None:
        caminho_i.append(current)
        current = caminho_i_dict.get(current)
    caminho_i.reverse()

    caminho_v = []
    current = meio_caminho
    current = caminho_v_dict.get(current)
    while current is not None:
        caminho_v.append(current)
        current = caminho_v_dict.get(current)

    return caminho_i + caminho_v 

def encontrar_caminho(labirinto_str):
    labirinto = _parse_labirinto(labirinto_str)
    start, end = procura_E_D(labirinto)

    fila_ida = deque([(start)])
    fila_volta = deque([(end)])

    caminho_i_dict = {start: None}
    caminho_v_dict = {end: None}

    visitado_ida = {start}
    visitado_volta = {end}

    meio_caminho = None

    while fila_ida and fila_volta:
        atual_ida = fila_ida.popleft()
        if atual_ida in visitado_volta:
            meio_caminho = atual_ida
            break

        for vizinho_ida in _vizinhos(labirinto, *atual_ida):
            if vizinho_ida not in visitado_ida:
                visitado_ida.add(vizinho_ida)
                caminho_i_dict[vizinho_ida] = atual_ida
                fila_ida.append(vizinho_ida)

        atual_volta = fila_volta.popleft()
        if atual_volta in visitado_ida:
            meio_caminho = atual_volta
            break

        for vizinho_volta in _vizinhos(labirinto, *atual_volta):
            if vizinho_volta not in visitado_volta:
                visitado_volta.add(vizinho_volta)
                caminho_v_dict[vizinho_volta] = atual_volta
                fila_volta.append(vizinho_volta)

    if meio_caminho:
        caminho_ida = []
        current = meio_caminho
        while current is not None:
            caminho_ida.append(current)
            current = caminho_i_dict.get(current)
        caminho_ida.reverse()

        caminho_volta = []
        current = meio_caminho
        while current is not None:
            caminho_volta.append(current)
            current = caminho_v_dict.get(current)
        
        caminho_volta.reverse()

        for r, c in caminho_ida:
            if labirinto[r][c] not in ['E', 'D']:
                labirinto[r][c] = '*'

        for r, c in caminho_volta:
            if (r,c) == meio_caminho:
                continue
            if labirinto[r][c] not in ['E', 'D']:
                labirinto[r][c] = '+'

        return "</br>".join(["".join(linha) for linha in labirinto])
    else:
        return "No path found.\n" + "\n".join(["".join(linha) for linha in labirinto])

def colorir_caminho(labirinto):
    COR_RESET = "</span>"
    COR_ENTRADA_SAIDA = "<span style='color:green !important;'>" # Verde
    COR_IDA = "<span style='color:yellow !important;'>" # Amarelo
    COR_VOLTA = "<span style='color:blue !important;'>" # Azul

    caminho_colorido = []
    for char in labirinto:
        if char == 'E' or char == 'D':
            caminho_colorido.append(f"{COR_ENTRADA_SAIDA}{char}{COR_RESET}")
        elif char == '*':
            caminho_colorido.append(f"{COR_IDA}{char}{COR_RESET}")
        elif char == '+':
            caminho_colorido.append(f"{COR_VOLTA}{char}{COR_RESET}")
        else:
            caminho_colorido.append(char)
    return "<span style='font-family:monospace;'>" + "".join(caminho_colorido) + "</span>"

st.markdown("""<style>.stTextArea textarea {font-family: monospace;}</style>""",unsafe_allow_html=True,)

labirinto = st.text_area("Mapa", placeholder="#####\n#...#\n#...#\n#...#\n#####")
st.html(colorir_caminho(encontrar_caminho(labirinto)))
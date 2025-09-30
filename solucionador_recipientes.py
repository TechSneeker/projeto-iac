from collections import deque
import heapq

#   x = quantidade no jarro de 5L
#   y = quantidade no jarro de 3L
# Ações:
#   - ('Fill', i)  -> enche jarro i até a capacidade
#   - ('Dump', i)  -> esvazia jarro i
#   - ('Pour', i, j) -> despeja de i em j o quanto couber

CAPACIDADE = (5, 3)
INICIO = (0, 0)
OBJETIVO = 4

def actions(state):
    x, y = state
    sizes = CAPACIDADE
    acts = []

    # Fill => encher
    if x < sizes[0]: acts.append(('Fill', 0))
    if y < sizes[1]: acts.append(('Fill', 1))

    # Dump => esvaziar
    if x > 0: acts.append(('Dump', 0))
    if y > 0: acts.append(('Dump', 1))

    # Pour (i -> j) => despejar
    if x > 0 and y < sizes[1]: acts.append(('Pour', 0, 1))
    if y > 0 and x < sizes[0]: acts.append(('Pour', 1, 0))

    return acts

def result(state, action):
    x, y = state
    sizes = CAPACIDADE
    act = action[0]

    if act == 'Fill':
        i = action[1]
        if i == 0:
            return (sizes[0], y)
        else:
            return (x, sizes[1])

    if act == 'Dump':
        i = action[1]
        if i == 0:
            return (0, y)
        else:
            return (x, 0)

    if act == 'Pour':
        i, j = action[1], action[2]
        if i == 0 and j == 1:
            # de x => y
            amount = min(x, sizes[1] - y)
            return (x - amount, y + amount)
        elif i == 1 and j == 0:
            # de y => x
            amount = min(y, sizes[0] - x)
            return (x + amount, y - amount)

    return state

def verificar_resultado_baldes(state):
    x, _ = state
    return x == OBJETIVO

def mensagem_formatada(s):
    return f"[5L:{s[0]} | 3L:{s[1]}]"


def reconstruir_sequencia_inicio_fim(parent, end):
    lista_estados = []
    cur = end
    while cur in parent and parent[cur][0] is not None:
        prev, act = parent[cur]
        lista_estados.append((cur, act))
        cur = prev
    lista_estados.reverse()
    return lista_estados

def busca_largura_cega(start):
    if verificar_resultado_baldes(start):
        return [], start

    frontier = deque([start])
    visited = set([start])
    parent = {start: (None, None)}

    while frontier:
        s = frontier.popleft()
        for a in actions(s):
            s2 = result(s, a)
            if s2 not in visited:
                parent[s2] = (s, a)
                if verificar_resultado_baldes(s2):
                    return reconstruir_sequencia_inicio_fim(parent, s2), s2
                visited.add(s2)
                frontier.append(s2)
    return None, None

def busca_profundidade_arvore(start, max_depth=10**9):
    parent = {start: (None, None)}
    found = [None]

    def dfs(s, depth, path_set):
        if verificar_resultado_baldes(s):
            found[0] = s
            return True
        if depth == 0:
            return False
        for a in actions(s):
            s2 = result(s, a)
            if s2 in path_set:
                continue 
            if s2 not in parent:
                parent[s2] = (s, a)
            path_set.add(s2)
            ok = dfs(s2, depth - 1, path_set)
            path_set.remove(s2)
            if ok:
                return True
        return False

    dfs(start, max_depth, set([start]))
    if found[0] is None:
        return None, None
    return reconstruir_sequencia_inicio_fim(parent, found[0]), found[0]

def busca_profundidade_limitada(start, limite=12):
    parent = {start: (None, None)}
    CUT = object()  # marcador interno

    def rec(s, depth, path_set):
        if verificar_resultado_baldes(s):
            return s
        if depth == 0:
            return CUT
        cutoff = False
        for a in actions(s):
            s2 = result(s, a)
            if s2 in path_set:
                continue
            if s2 not in parent:
                parent[s2] = (s, a)
            path_set.add(s2)
            r = rec(s2, depth - 1, path_set)
            path_set.remove(s2)
            if r is CUT:
                cutoff = True
            elif r is not None:
                return r
        return CUT if cutoff else None

    res = rec(start, limite, set([start]))
    if res is CUT:
        return 'cutoff', None
    if res is None:
        return None, None
    return reconstruir_sequencia_inicio_fim(parent, res), res

def aprofundamento_iterativo(start, limite_max=30):
    for d in range(limite_max + 1):
        ans, end = busca_profundidade_limitada(start, d)
        if ans not in (None, 'cutoff'):
            return ans, end
    return None, None

def busca_profundidade_cega(start, max_nodes=10000):
    stack = [start]
    visited = set([start])
    parent = {start: (None, None)}
    nodes = 0

    while stack and nodes < max_nodes:
        s = stack.pop()
        nodes += 1
        if verificar_resultado_baldes(s):
            return reconstruir_sequencia_inicio_fim(parent, s), s
        for a in actions(s):
            s2 = result(s, a)
            if s2 not in visited:
                visited.add(s2)
                parent[s2] = (s, a)
                stack.append(s2)
    return None, None

# -----------------------------
# Heurísticas
# -----------------------------
def heuristica_conservadora(state):
    """Heurística conservadora (admissível):
    aprox. nº mínimo de passos úteis com base na diferença de litros no jarro alvo.
    Usa floor(|x-4|/3), pois o jarro auxiliar tem 3L, e uma 'transferência útil' muda o alvo em ≤ 3L.
    """
    x, _ = state
    return abs(x - OBJETIVO) // 3

def h_bool(state):
    #0 = objetivo 1 - não
    return 0 if verificar_resultado_baldes(state) else 1

def h_zero(state):
    return 0

def busca_gulosa(start, hfn):
    frontier = []
    heapq.heappush(frontier, (hfn(start), start))
    parent = {start: (None, None)}
    visited = set()

    while frontier:
        _, s = heapq.heappop(frontier)
        if verificar_resultado_baldes(s):
            return reconstruir_sequencia_inicio_fim(parent, s), s
        if s in visited:
            continue
        visited.add(s)
        for a in actions(s):
            s2 = result(s, a)
            if s2 not in visited:
                parent[s2] = (s, a)
                heapq.heappush(frontier, (hfn(s2), s2))
    return None, None

def astar(start, hfn):
    g = {start: 0}
    frontier = []
    heapq.heappush(frontier, (hfn(start), 0, start))
    parent = {start: (None, None)}
    closed = set()

    while frontier:
        f, g_s, s = heapq.heappop(frontier)
        if verificar_resultado_baldes(s):
            return reconstruir_sequencia_inicio_fim(parent, s), s
        if s in closed:
            continue
        closed.add(s)

        for a in actions(s):
            s2 = result(s, a)
            tentative_g = g_s + 1  #custo por ação
            if s2 not in g or tentative_g < g[s2]:
                g[s2] = tentative_g
                parent[s2] = (s, a)
                f2 = tentative_g + hfn(s2)
                heapq.heappush(frontier, (f2, tentative_g, s2))
    return None, None

def print_solution(path):
    if not path:
        print("Nenhum passo (já estava no objetivo?)")
        return
    s0 = INICIO
    print(f"Estado inicial: {mensagem_formatada(s0)}")
    step = 1
    for s, a in path:
        if a[0] == 'Pour':
            txt = f"Passo {step:02d}: Pour {a[1]} -> {a[2]} -> {mensagem_formatada(s)}"
        else:
            txt = f"Passo {step:02d}: {a[0]}({a[1]}) -> {mensagem_formatada(s)}"
        print(txt)
        step += 1
    print(f"\nObjetivo atingido? {verificar_resultado_baldes(path[-1][0])} | Estado final: {mensagem_formatada(path[-1][0])}")
    print(f"Total de passos: {len(path)}")
def menu():
    print("="*60)
    print(" Problema dos Recipientes (5L, 3L) -> objetivo: 4L no jarro de 5L ")
    print("="*60)
    print("Escolha o algoritmo:")
    print(" 1) Busca em Largura (BFS) [Cega, ótima em nº de passos]")
    print(" 2) Busca em Profundidade (DFS - grafo) [Cega, não ótima]")
    print(" 6) Busca em Profundidade (DFS - árvore) [variação]")
    print(" 7) Profundidade Limitada (DLS)")
    print(" 8) Aprofundamento Iterativo (IDDFS)")
    print(" 3) Busca Gulosa (heurística h_liters)")
    print(" 4) A* (heurística h_liters)  [Informada]")
    print(" 5) A* (heurística zero)      [Vira custo uniforme]")
    print(" q) Sair")
    return input("Opção: ").strip().lower()


def run():
    while True:
        op = menu()
        if op == 'q':
            print("Saindo...")
            break

        if op == '1':
            path, _ = busca_largura_cega(INICIO)
            print("\n== BFS ==")
            print("Sem solução." if path is None else print_solution(path))

        elif op == '2':
            path, _ = busca_profundidade_cega(INICIO)
            print("\n== DFS (grafo) ==")
            print("Sem solução (ou limite)." if path is None else print_solution(path))

        elif op == '6':
            path, _ = busca_profundidade_arvore(INICIO)
            print("\n== DFS (árvore) ==")
            print("Sem solução." if path is None else print_solution(path))

        elif op == '7':
            # pergunta leve com default (CLI)
            try:
                lim_txt = input("Limite de profundidade (default=12): ").strip()
                limite = int(lim_txt) if lim_txt else 12
            except:
                limite = 12
            ans, _ = busca_profundidade_limitada(INICIO, limite)
            print(f"\n== DLS (limite={limite}) ==")
            if ans == 'cutoff':
                print("Cutoff (limite atingido, sem solução neste limite).")
            elif ans is None:
                print("Sem solução.")
            else:
                print_solution(ans)

        elif op == '8':
            try:
                lim_txt = input("Limite máximo do IDDFS (default=30): ").strip()
                limite_max = int(lim_txt) if lim_txt else 30
            except:
                limite_max = 30
            path, _ = aprofundamento_iterativo(INICIO, limite_max)
            print(f"\n== IDDFS (até {limite_max}) ==")
            print("Sem solução." if path is None else print_solution(path))

        elif op == '3':
            path, _ = busca_gulosa(INICIO, heuristica_conservadora)
            print("\n== Gulosa (h_liters) ==")
            print("Sem solução." if path is None else print_solution(path))

        elif op == '4':
            path, _ = astar(INICIO, heuristica_conservadora)
            print("\n== A* (h_liters) ==")
            print("Sem solução." if path is None else print_solution(path))

        elif op == '5':
            path, _ = astar(INICIO, h_zero)
            print("\n== A* (h_zero) ==")
            print("Sem solução." if path is None else print_solution(path))

        else:
            print("Opção inválida.")

if __name__ == "__main__":
    run()
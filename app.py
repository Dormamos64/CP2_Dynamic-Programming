import functools
import time
import tracemalloc
import folium

# ==============================================================================
# 1. MODELAGEM DOS GRAFOS (Nós >= 15 por cidade) [cite: 21]
# ==============================================================================

grafos = {
    "Beijing": {
        "Sihui East": [("Sihui", 2)],
        "Sihui": [("Sihui East", 2), ("Dawanglu", 3)],
        "Dawanglu": [("Sihui", 3), ("Guomao", 2)],
        "Guomao": [("Dawanglu", 2), ("Jianguomen", 4), ("Hujialou", 3)],
        "Hujialou": [("Guomao", 3), ("Tuanjiehu", 2)],
        "Tuanjiehu": [("Hujialou", 2), ("Sanyuanqiao", 5)],
        "Sanyuanqiao": [("Tuanjiehu", 5), ("Shaoyaoju", 4)],
        "Shaoyaoju": [("Sanyuanqiao", 4), ("Zhichunlu", 8)],
        "Zhichunlu": [("Shaoyaoju", 8), ("Xizhimen", 5)],
        "Jianguomen": [("Guomao", 4), ("Dongdan", 2), ("Chaoyangmen", 3)],
        "Dongdan": [("Jianguomen", 2), ("Wangfujing", 2)],
        "Wangfujing": [("Dongdan", 2), ("Tiananmen East", 2)],
        "Tiananmen East": [("Wangfujing", 2), ("Xidan", 4)],
        "Xidan": [("Tiananmen East", 4), ("Fuxingmen", 3), ("Xuanwumen", 2)],
        "Xuanwumen": [("Xidan", 2), ("Hepingmen", 2)],
        "Hepingmen": [("Xuanwumen", 2), ("Qianmen", 2)],
        "Chaoyangmen": [("Jianguomen", 3), ("Dongsi", 3)],
        "Fuxingmen": [("Xidan", 3), ("Fuchengmen", 3)],
        "Fuchengmen": [("Fuxingmen", 3), ("Chegongzhuang", 2)],
        "Chegongzhuang": [("Fuchengmen", 2), ("Xizhimen", 2)],
        "Xizhimen": [("Chegongzhuang", 2), ("Zhichunlu", 5)]
    },
    "San Francisco": {
        "Dublin/Pleasanton": [("West Dublin", 3)],
        "West Dublin": [("Dublin/Pleasanton", 3), ("Castro Valley", 10)],
        "Castro Valley": [("West Dublin", 10), ("Bay Fair", 8)],
        "Bay Fair": [("Castro Valley", 8), ("San Leandro", 5), ("Hayward", 6)],
        "San Leandro": [("Bay Fair", 5), ("Coliseum", 6)],
        "Coliseum": [("San Leandro", 6), ("Fruitvale", 5)],
        "Fruitvale": [("Coliseum", 5), ("Lake Merritt", 6)],
        "Lake Merritt": [("Fruitvale", 6), ("West Oakland", 5)],
        "West Oakland": [("Lake Merritt", 5), ("Embarcadero", 10), ("12th St Oakland", 4)],
        "12th St Oakland": [("West Oakland", 4), ("19th St Oakland", 2)],
        "19th St Oakland": [("12th St Oakland", 2), ("MacArthur", 3)],
        "MacArthur": [("19th St Oakland", 3), ("Rockridge", 5)],
        "Embarcadero": [("West Oakland", 10), ("Montgomery St", 2)],
        "Montgomery St": [("Embarcadero", 2), ("Powell St", 2)],
        "Powell St": [("Montgomery St", 2), ("Civic Center", 2)],
        "Civic Center": [("Powell St", 2), ("16th St Mission", 3)],
        "16th St Mission": [("Civic Center", 3), ("24th St Mission", 2)],
        "24th St Mission": [("16th St Mission", 2), ("Glen Park", 4)],
        "Glen Park": [("24th St Mission", 4), ("Balboa Park", 3)],
        "Balboa Park": [("Glen Park", 3), ("Daly City", 3)],
        "Daly City": [("Balboa Park", 3)]
    },
    "Sao Paulo": { 
        "Tucuruvi": [("Parada Inglesa", 3)],
        "Parada Inglesa": [("Tucuruvi", 3), ("Jardim Sao Paulo", 2)],
        "Jardim Sao Paulo": [("Parada Inglesa", 2), ("Santana", 3)],
        "Santana": [("Jardim Sao Paulo", 3), ("Carandiru", 2)],
        "Carandiru": [("Santana", 2), ("Portuguesa-Tiete", 2)],
        "Portuguesa-Tiete": [("Carandiru", 2), ("Armenia", 3)],
        "Armenia": [("Portuguesa-Tiete", 3), ("Luz", 4)],
        "Luz": [("Armenia", 4), ("Sao Bento", 2), ("Republica", 5)],
        "Sao Bento": [("Luz", 2), ("Se", 2)],
        "Se": [("Sao Bento", 2), ("Liberdade", 2)],
        "Liberdade": [("Se", 2), ("Paraiso", 4)],
        "Paraiso": [("Liberdade", 4), ("Ana Rosa", 2)],
        "Ana Rosa": [("Paraiso", 2), ("Vila Mariana", 3)],
        "Vila Mariana": [("Ana Rosa", 3), ("Santa Cruz", 3)],
        "Santa Cruz": [("Vila Mariana", 3), ("Hospital Sao Paulo", 3)],
        "Republica": [("Luz", 5), ("Santa Cruz", 15)],
        "Hospital Sao Paulo": [("Santa Cruz", 3), ("AACD-Servidor", 3)],
        "AACD-Servidor": [("Hospital Sao Paulo", 3), ("Moema", 3)],
        "Moema": [("AACD-Servidor", 3), ("Eucaliptos", 3)],
        "Eucaliptos": [("Moema", 3), ("Campo Belo", 4)],
        "Campo Belo": [("Eucaliptos", 4), ("Brooklin", 3)],
        "Brooklin": [("Campo Belo", 3), ("Santo Amaro", 5)],
        "Santo Amaro": [("Brooklin", 5), ("Giovanni Gronchi", 3)],
        "Giovanni Gronchi": [("Santo Amaro", 3), ("Vila das Belezas", 2)],
        "Vila das Belezas": [("Giovanni Gronchi", 2), ("Capao Redondo", 4)],
        "Capao Redondo": [("Vila das Belezas", 4)]
    }
}

# Coordenadas aproximadas para o Folium [cite: 29]
coords = {
    "Beijing": {
        "Sihui East": [39.908, 116.514], "Xizhimen": [39.940, 116.355],
        "Guomao": [39.908, 116.460], "Jianguomen": [39.908, 116.435]
    },
    "San Francisco": {
        "Dublin/Pleasanton": [37.701, -121.899], "Daly City": [37.706, -122.469],
        "West Oakland": [37.804, -122.295], "Embarcadero": [37.792, -122.397]
    },
    "Sao Paulo": {
        "Tucuruvi": [-23.480, -46.603], "Capao Redondo": [-23.659, -46.768],
        "Luz": [-23.536, -46.634], "Santa Cruz": [-23.598, -46.636]
    }
}

# ==============================================================================
# 2. LÓGICA DE CUSTO E ALGORITMOS [cite: 23, 24, 25, 37]
# ==============================================================================

def get_fator(horario):
    """Implementa a tabela de bônus e penalidades [cite: 37]"""
    if 5 <= horario < 7: return 0.6
    if 7 <= horario < 9: return 1.5
    if 17 <= horario <= 20: return 2.0
    return 1.0

def resolver_cidade(nome_cidade, origem, destino, horario):
    grafo = grafos[nome_cidade]
    fator = get_fator(horario)

    # 1. Menor Caminho com Memoização [cite: 23, 43]
    @functools.lru_cache(maxsize=None)
    def menor_custo(u, v, visitados=frozenset()):
        if u == v: return 0, (v,)
        melhor_c = float('inf')
        melhor_p = ()
        for vizinho, peso in grafo.get(u, []):
            if vizinho not in visitados:
                c, p = menor_custo(vizinho, v, visitados | {u})
                custo_total = (peso * fator) + c
                if custo_total < melhor_c:
                    melhor_c, melhor_p = custo_total, (u,) + p
        return melhor_c, melhor_p

    # 2. Caminho Mais Longo Simples (Backtracking) [cite: 24]
    def maior_custo(u, v, visitados=None):
        if visitados is None: visitados = set()
        if u == v: return 0, (v,)
        visitados.add(u)
        pior_c, pior_p = -1, ()
        for vizinho, peso in grafo.get(u, []):
            if vizinho not in visitados:
                c, p = maior_custo(vizinho, v, visitados)
                if c != -1:
                    custo_total = (peso * fator) + c
                    if custo_total > pior_c:
                        pior_c, pior_p = custo_total, (u,) + p
        visitados.remove(u) # Backtracking
        return pior_c, pior_p

    # Análise de Desempenho [cite: 27, 56, 63]
    tracemalloc.start()
    t0 = time.perf_counter()
    res_min = menor_custo(origem, destino)
    t_min = time.perf_counter() - t0
    mem_min = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()

    res_max = maior_custo(origem, destino)

    print(f"\n--- RESULTADOS: {nome_cidade} ({horario}h) ---")
    print(f"MAIS CURTO: Custo {res_min[0]:.2f} | Tempo {t_min:.6f}s | Memória {mem_min/1024:.2f}KB")
    print(f"MAIS LONGO: Custo {res_max[0]:.2f}")
    
    # Retorna dicionário para evitar erro de índice de tupla
    return {
        "rota_min": res_min[1],
        "custo_min": res_min[0],
        "rota_max": res_max[1],
        "custo_max": res_max[0],
        "fator_aplicado": fator
    }

# Execuções Iniciais
resultado_bj = resolver_cidade("Beijing", "Sihui East", "Xizhimen", 18)
resultado_sf = resolver_cidade("San Francisco", "Dublin/Pleasanton", "Daly City", 8)
resultado_sp = resolver_cidade("Sao Paulo", "Tucuruvi", "Capao Redondo", 18)




----------------------
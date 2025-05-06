import threading
import time
import random

NUM_ANDARES = 10
CAPACIDADE_ELEVADOR = 5
TOTAL_PASSAGEIROS = 10

fila_espera = {i: [] for i in range(NUM_ANDARES)}
passageiros_atendidos = 0
inicio_simulacao = None
fim_simulacao = None
passageiro_counter = 1

class Elevador(threading.Thread):
    def __init__(self, id, estrategia):
        super().__init__()
        self.id = id
        self.andar_atual = 0
        self.passageiros = []
        self.estrategia = estrategia

    def run(self):
        global passageiros_atendidos, fim_simulacao
        while True:
            if passageiros_atendidos >= TOTAL_PASSAGEIROS:
                return
            waiting_calls = [(andar, fila_espera[andar]) for andar in fila_espera if fila_espera[andar]]
            if waiting_calls:
                waiting_calls.sort(key=lambda x: abs(self.andar_atual - x[0]))
                destino, lista_passageiros = waiting_calls[0]
                self.mover_para(destino)
                self.embarcar(lista_passageiros)
                self.levar_passageiros()
            else:
                time.sleep(0.5)

    def mover_para(self, andar):
        time.sleep(abs(self.andar_atual - andar) * 0.2)
        self.andar_atual = andar

    def embarcar(self, lista_passageiros):
        current_time = time.time()
        if self.estrategia == "SJF":
            lista_passageiros.sort(key=lambda p: p.tempo_estimado)
        elif self.estrategia == "PS":
            lista_passageiros.sort(key=lambda p: current_time - p.criacao, reverse=True)

        while lista_passageiros and len(self.passageiros) < CAPACIDADE_ELEVADOR:
            passageiro = lista_passageiros.pop(0)
            self.passageiros.append(passageiro)
            espera = current_time - passageiro.criacao
            print(f"[ELEVADOR {self.id}] Passageiro {passageiro.id} embarcou (Espera: {espera:.2f}s, Origem: {passageiro.origem}, Destino: {passageiro.destino})")

    def levar_passageiros(self):
        global passageiros_atendidos, fim_simulacao
        while self.passageiros:
            passageiro = self.passageiros.pop(0)
            self.mover_para(passageiro.destino)
            passageiros_atendidos += 1
            print(f"[ELEVADOR {self.id}] Passageiro {passageiro.id} desembarcou no andar {passageiro.destino}. Total atendidos: {passageiros_atendidos}")
            if passageiros_atendidos == TOTAL_PASSAGEIROS:
                fim_simulacao = time.time()

class Passageiro:
    def __init__(self, id, origem, destino):
        self.id = id
        self.origem = origem
        self.destino = destino
        self.tempo_estimado = abs(destino - origem)
        self.criacao = time.time()  # usado como base para tempo de espera

def gerar_passageiros():
    global passageiro_counter
    gerados = 0
    while gerados < TOTAL_PASSAGEIROS:
        origem = random.randint(0, NUM_ANDARES - 1)
        destino = random.randint(0, NUM_ANDARES - 1)
        if origem != destino:
            novo_passageiro = Passageiro(passageiro_counter, origem, destino)
            passageiro_counter += 1
            fila_espera[origem].append(novo_passageiro)
            print(f"[GERADOR] Passageiro {novo_passageiro.id} criado (Origem: {origem}, Destino: {destino})")
            gerados += 1
            time.sleep(random.uniform(0.3, 1.0))

def simular_elevadores(num_elevadores, estrategia):
    global fila_espera, passageiros_atendidos, inicio_simulacao, fim_simulacao, passageiro_counter
    fila_espera = {i: [] for i in range(NUM_ANDARES)}
    passageiros_atendidos = 0
    passageiro_counter = 1
    inicio_simulacao = time.time()
    fim_simulacao = None

    random.seed(42)

    print(f"\n=== Simulação {estrategia} com {num_elevadores} elevador(es) ===")
    elevadores = [Elevador(i, estrategia) for i in range(num_elevadores)]
    for elevador in elevadores:
        elevador.start()

    gerador = threading.Thread(target=gerar_passageiros)
    gerador.start()

    for elevador in elevadores:
        elevador.join()
    gerador.join()

    tempo_total = fim_simulacao - inicio_simulacao if fim_simulacao else 0
    print(f"=== Fim da simulação ({estrategia}) em {tempo_total:.2f} segundos ===\n")
    return tempo_total

# Comparação entre SJF e PS
for estrategia in ["SJF", "PS"]:
    simular_elevadores(num_elevadores=2, estrategia=estrategia)

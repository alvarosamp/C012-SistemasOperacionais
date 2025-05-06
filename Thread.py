import threading
import time
import random

NUM_ANDARES = 10
CAPACIDADE_ELEVADOR = 5
TOTAL_PASSAGEIROS = 100

fila_espera = {i: [] for i in range(NUM_ANDARES)}
passageiros_atendidos = 0
inicio_simulacao = None
fim_simulacao = None
passageiro_counter = 1
usar_semaforo = True
fila_lock = threading.Lock() if usar_semaforo else None

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
            if fila_lock:
                with fila_lock:
                    waiting_calls = [(andar, fila_espera[andar]) for andar in fila_espera if fila_espera[andar]]
            else:
                waiting_calls = [(andar, fila_espera[andar]) for andar in fila_espera if fila_espera[andar]]

            if waiting_calls:
                waiting_calls.sort(key=lambda x: abs(self.andar_atual - x[0]))
                destino, lista_passageiros = waiting_calls[0]

                if not usar_semaforo and len(lista_passageiros) > CAPACIDADE_ELEVADOR:
                    excesso = len(lista_passageiros) - CAPACIDADE_ELEVADOR
                    penalidade = excesso * 0.5
                    print(f"[ELEVADOR {self.id}] Penalidade antes do movimento: {excesso} excedentes -> {penalidade:.2f}s")
                    time.sleep(penalidade)

                self.mover_para(destino)
                self.embarcar(lista_passageiros)
                self.levar_passageiros()
            else:
                time.sleep(0.1)

    def mover_para(self, andar):
        time.sleep(abs(self.andar_atual - andar) * 0.05)
        self.andar_atual = andar

    def embarcar(self, lista_passageiros):
        current_time = time.time()
        if fila_lock:
            with fila_lock:
                self._embarcar_passageiros(lista_passageiros, current_time)
        else:
            self._embarcar_passageiros(lista_passageiros, current_time)

    def _embarcar_passageiros(self, lista_passageiros, current_time):
        if self.estrategia == "SJF":
            lista_passageiros.sort(key=lambda p: p.tempo_estimado)
        elif self.estrategia == "PS":
            lista_passageiros.sort(key=lambda p: current_time - p.criacao, reverse=True)

        if not usar_semaforo and len(lista_passageiros) > CAPACIDADE_ELEVADOR:
            excesso = len(lista_passageiros) - CAPACIDADE_ELEVADOR
            penalidade = excesso * 0.5
            print(f"[ELEVADOR {self.id}] Penalidade durante embarque: {excesso} excedentes -> {penalidade:.2f}s")
            time.sleep(penalidade)

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
            if fila_lock:
                with fila_lock:
                    passageiros_atendidos += 1
                    if passageiros_atendidos == TOTAL_PASSAGEIROS:
                        fim_simulacao = time.time()
            else:
                passageiros_atendidos += 1
                if passageiros_atendidos == TOTAL_PASSAGEIROS:
                    fim_simulacao = time.time()
            print(f"[ELEVADOR {self.id}] Passageiro {passageiro.id} desembarcou no andar {passageiro.destino}. Total atendidos: {passageiros_atendidos}")

class Passageiro:
    def __init__(self, id, origem, destino):
        self.id = id
        self.origem = origem
        self.destino = destino
        self.tempo_estimado = abs(destino - origem)
        self.criacao = time.time()

def gerar_passageiros():
    global passageiro_counter
    gerados = 0
    while gerados < TOTAL_PASSAGEIROS:
        origem = random.randint(0, NUM_ANDARES - 1)
        destino = random.randint(0, NUM_ANDARES - 1)
        if origem != destino:
            novo_passageiro = Passageiro(passageiro_counter, origem, destino)
            passageiro_counter += 1
            if fila_lock:
                with fila_lock:
                    fila_espera[origem].append(novo_passageiro)
            else:
                fila_espera[origem].append(novo_passageiro)
            print(f"[GERADOR] Passageiro {novo_passageiro.id} criado (Origem: {origem}, Destino: {destino})")
            gerados += 1
            time.sleep(random.uniform(0.01, 0.05))

def simular_elevadores(num_elevadores, estrategia, com_semaforo):
    global fila_espera, passageiros_atendidos, inicio_simulacao, fim_simulacao, passageiro_counter, fila_lock, usar_semaforo

    usar_semaforo = com_semaforo
    fila_lock = threading.Lock() if usar_semaforo else None

    fila_espera = {i: [] for i in range(NUM_ANDARES)}
    passageiros_atendidos = 0
    passageiro_counter = 1
    inicio_simulacao = time.time()
    fim_simulacao = None

    random.seed(42)

    modo = "COM SEMAFORO" if com_semaforo else "SEM SEMAFORO"
    print(f"\n=== Simulacao {estrategia} ({modo}) com {num_elevadores} elevador(es) ===")
    elevadores = [Elevador(i, estrategia) for i in range(num_elevadores)]
    for elevador in elevadores:
        elevador.start()

    gerador = threading.Thread(target=gerar_passageiros)
    gerador.start()

    for elevador in elevadores:
        elevador.join()
    gerador.join()

    tempo_total = fim_simulacao - inicio_simulacao if fim_simulacao else 0
    print(f"=== Fim da simulacao ({estrategia}, {modo}) em {tempo_total:.2f} segundos ===\n")
    return tempo_total

tempos_sjf = {
    "com_semaforo": simular_elevadores(num_elevadores=4, estrategia="SJF", com_semaforo=True),
    "sem_semaforo": simular_elevadores(num_elevadores=4, estrategia="SJF", com_semaforo=False)
}

tempos_ps = {
    "com_semaforo": simular_elevadores(num_elevadores=4, estrategia="PS", com_semaforo=True),
    "sem_semaforo": simular_elevadores(num_elevadores=4, estrategia="PS", com_semaforo=False)
}

print("\n=== COMPARACAO FINAL ===")
print(f"SJF - Com Semaforo: {tempos_sjf['com_semaforo']:.2f}s | Sem Semaforo: {tempos_sjf['sem_semaforo']:.2f}s")
print(f"PS  - Com Semaforo: {tempos_ps['com_semaforo']:.2f}s | Sem Semaforo: {tempos_ps['sem_semaforo']:.2f}s")
print("\n=== FIM DA SIMULACAO ===")
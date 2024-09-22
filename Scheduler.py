from matplotlib import pyplot as plt


class Processo:
    nome: str
    surto_cpu: int
    tempo_e_s: int
    tempo_total_cpu: int
    ordem: int
    prioridade: int
    tempo_executado: int
    estado: str
    credito: int

    """Construtor da classe Processo"""
    def __init__(self, nome, surto_cpu, tempo_e_s, tempo_total_cpu, ordem, prioridade):
        self.nome = nome                          # Nome do processo
        self.surto_cpu = surto_cpu                # Surto de CPU (caso o processo tenha operação de I/O)
        self.tempo_exec_surto = 0                 # Tempo de execução no surto atual
        self.tempo_e_s = tempo_e_s                # Tempo de operação de I/O (E/S)
        self.tempo_total_cpu = tempo_total_cpu    # Tempo total de CPU necessário
        self.ordem = ordem                        # Ordem de execução (usada para desempate)
        self.prioridade = prioridade              # Prioridade do processo
        self.tempo_executado = 0                  # Tempo já executado pelo processo
        self.estado = "Ready"                     # Estado inicial do processo (Ready)
        self.credito = prioridade                 # Crédito inicial do processo (igual à prioridade)

    """To String"""
    def __str__(self):
        return (f"Processo {self.nome} : "
                f"Surto de CPU- {self.surto_cpu}, "
                f"surto atual- {self.tempo_exec_surto}, "
                f"Tempo de E/S- {self.tempo_e_s}, "
                f"executado- {self.tempo_executado}, "
                f"Estado atual- {self.estado}, "
                f"Crédito atual- {self.credito}")

class Escalonador:
    processos: list[Processo]
    ready: list[Processo]
    blocked: dict[Processo, int]
    running: dict[Processo, int]
    estados: dict[str, list[str]]
    processos_finalizados: int


    """Construtor da classe Escalonador"""
    def __init__(self, processos: list[Processo]) -> None:
        self.processos = processos
        self.ready = self.ordena_fila(processos)
        self.blocked = {}
        self.running = {}
        self.estados_historico = {p.nome: ["Ready"] for p in processos}        
        self.processos_finalizados = 0
        self.estados = {p.nome: ["Ready"] for p in processos} 
        self.historico_creditos = {p.nome: [p.credito] for p in processos} 



    """Ordena a fila de processos"""
    def ordena_fila(self, processos: list[Processo]) -> list[Processo]:
        return sorted(processos, key=lambda p: (p.credito, -p.ordem), reverse=True)
    
    """Verifica os créditos dos processos"""
    def check_credits(self) -> list[Processo]:
        processos_em_ready = list(filter(lambda p: p.estado == "Ready", self.processos))

        # Se todos os processos em 'Ready' estão com crédito zero, os créditos são atualizados
        if processos_em_ready and all(p.credito == 0 for p in processos_em_ready):
            for p in self.processos:
                # Atualiza o crédito: reduz o crédito à metade e soma com a prioridade
                p.credito = (p.credito // 2) + p.prioridade
        return processos
    
    
    """Executa o processo"""
    def run(self, processo) -> None:        
        processo.credito -= 1  # Reduz o crédito
        processo.tempo_executado += 1  # Incrementa o tempo executado
        tem_op_IO = processo.tempo_e_s != 0
        if tem_op_IO:
            processo.tempo_exec_surto += 1  # Incrementa o tempo de surto

    """Inicia a execução dos processos"""
    def start(self) -> dict[str, list[str]]:
        processo_eleito = self.ordena_fila(self.ready)[0]
        self.running[processo_eleito.nome] = processo_eleito.surto_cpu if processo_eleito.surto_cpu != 0 else processo_eleito.credito
        self.ready.remove(processo_eleito)
        processo_eleito.estado = "Running"


        count = 0
        while self.processos_finalizados < len(self.processos):
            for p in list(self.blocked.keys()):
                self.blocked[p] -= 1
                if self.blocked[p] == 0:
                    p.estado = "Ready"
                    self.ready.append(p)  # Move de bloqueado para pronto
                    del self.blocked[p]

            self.check_credits()
    
            # verifica se o processo atual tem tempo de surto ainda ou credito
            if processo_eleito is None or self.running[processo_eleito.nome] <= 0 or processo_eleito.credito == 0:
                # caso não tenha mais tempo, tem q eleger um novo lider
               
                # elege novo processo caso tenha processo em ready
                teve_eleicao = False
                if self.ready:
                    teve_eleicao = True
                    novo_processo_eleito = self.ordena_fila(self.ready)[0]
                    
                    if processo_eleito is not None:
                        del self.running[processo_eleito.nome]

                        if processo_eleito.tempo_e_s != 0 and processo_eleito.tempo_exec_surto == processo_eleito.surto_cpu:
                            self.blocked[processo_eleito] = processo_eleito.tempo_e_s
                            processo_eleito.tempo_exec_surto = 0
                            processo_eleito.estado = "Blocked"
                        elif processo_eleito.tempo_executado == processo_eleito.tempo_total_cpu:
                            processo_eleito.estado = "Exit"
                            self.processos_finalizados += 1
                        else:
                            self.ready.append(processo_eleito)
                            processo_eleito.estado = "Ready"

                    # trocando o processo eleito
                    processo_eleito = novo_processo_eleito
                     
                    self.running[processo_eleito.nome] = processo_eleito.surto_cpu if processo_eleito.surto_cpu != 0 else processo_eleito.credito
                    self.ready.remove(processo_eleito)
                    processo_eleito.estado = "Running"
                else:
                    novo_processo_eleito = None

                if processo_eleito is not None and not teve_eleicao:
                    # remove da lista de execucao o processo atual
                    del self.running[processo_eleito.nome]
                    
                    # verifica para qual estado esse processo deve ir
                    if processo_eleito.tempo_e_s != 0 and processo_eleito.tempo_exec_surto == processo_eleito.surto_cpu:
                        self.blocked[processo_eleito] = processo_eleito.tempo_e_s
                        processo_eleito.tempo_exec_surto = 0
                        processo_eleito.estado = "Blocked"  
                    else:
                        self.ready.append(processo_eleito)
                        processo_eleito.estado = "Ready"
                
                processo_eleito = novo_processo_eleito
                
                teve_eleicao = False

            if processo_eleito is not None:
                # roda o novo processo
                self.run(processo_eleito)
                # reduz uma unidade de execucao
                self.running[processo_eleito.nome] -= 1
            
                if processo_eleito.tempo_executado == processo_eleito.tempo_total_cpu:
                   processo_eleito.estado = "Exit"
                   self.processos_finalizados += 1
                   del self.running[processo_eleito.nome]
                   processo_eleito = None

            for p in self.processos:
               self.estados[p.nome].append(p.estado)
               self.historico_creditos[p.nome].append(p.credito)

            print(f"Processos em Ready: {[p.nome for p in self.ready]}")
            print(f"Processos em Blocked: {[p.nome for p in self.blocked.keys()]}")
            print(f"Processos em Running: {[p for p in self.running.keys()]}")
            print(f"Processos finalizados: {self.processos_finalizados}")
            print(f"\n")
    
            count+=1
            print(count)
        
        return self.estados, self.historico_creditos
    

def plot_process_states(process_states, process_states_values) -> None:
    state_colors = {
        'Running': 'lightblue',
        'Ready': 'lightgreen',
        'Blocked': 'yellow',
        'Exit': 'red'
    }

    fig, ax = plt.subplots(figsize=(10, 6))

    for i, (process, states) in enumerate(process_states.items()):
        for j, state in enumerate(states):
            ax.broken_barh([(j, 1)], (i - 0.4, 0.8), facecolors=state_colors[state], edgecolors='black')
            if j < len(process_states_values[process]):
                ax.text(j + 0.5, i, str(process_states_values[process][j]), va='center', ha='center', color='black')

    ax.set_yticks(range(len(process_states)))
    ax.set_yticklabels(process_states.keys())
    ax.set_xticks(range(len(next(iter(process_states.values())))))
    ax.set_xlabel('Time')
    ax.set_ylabel('Processes')

    legend_elements = [plt.Rectangle((0, 0), 1, 1, color=color, label=state)
                       for state, color in state_colors.items()]
    ax.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.title('Process State Over Time')
    plt.gca().invert_yaxis()
    plt.show()

# Execução do programa
if __name__ == "__main__":
    # Cria uma lista de processos
    processos = [
        Processo(nome="A", surto_cpu=2, tempo_e_s=5,
                 tempo_total_cpu=6, ordem=1, prioridade=3), 
        Processo(nome="B", surto_cpu=3, tempo_e_s=10,
                 tempo_total_cpu=6, ordem=2, prioridade=3),
        Processo(nome="C", surto_cpu=0, tempo_e_s=0,
                    tempo_total_cpu=14, ordem=3, prioridade=3),
        Processo(nome="D", surto_cpu=0, tempo_e_s=0,
                    tempo_total_cpu=10, ordem=4, prioridade=3),
    ]

    escalonador_de_processos = Escalonador(processos)
    estados, es = escalonador_de_processos.start()
    print(es)
    plot_process_states(estados,es)
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import os, re, time, math

# Importa os componentes visuais que você já modularizou em outro arquivo
from gui_components import ToolTip, EditorComLinhas, DicionarioComandos
# Importa a classe responsável por conversar com o microcontrolador via USB
from serial_manager import GerenciadorSerial

class RobixSupervisorio(ctk.CTk):
    def __init__(self):
        super().__init__()
        # --- 1. Configurações Básicas da Janela ---
        self.title("Supervisório Robix - IFMT")
        self.geometry("1100x850")
        self.configure(fg_color="#1E1E1E") # Fundo escuro padrão industrial
        
        # --- 2. Variáveis de Estado e Controle do Sistema ---
        self.botoes_dinamicos = {}
        self.parar_execucao = False # Flag crítica de segurança (Parada de Emergência)
        self.rotina_gravada = []    # Memória temporária para os pontos do Teach Pendant
        
        # Variáveis atreladas à interface (Checkbox/Switches)
        self.var_tempo_real = tk.BooleanVar(value=False)
        self.var_debug_serial = tk.BooleanVar(value=True) 
        
        # Controle de tempo para evitar "sufocar" a porta serial enviando dados rápido demais
        self.tempos_motores = [0.0] * 6 

        self.motor_selecionado_idx = 0 # Qual motor está selecionado no teclado
        self.frames_motores = []       # Guarda os widgets dos sliders para mudar a borda deles
        self.metodos_salvos = {}       # Dicionário que guarda as funções customizadas pelo usuário

        # --- 3. Gerenciamento da Comunicação Serial ---
        self.porta_serial = GerenciadorSerial()
        self.porta_selecionada = tk.StringVar(value="Conectar USB")
        self.lista_combos_portas = [] # Lista de dropdowns de porta COM para atualizar todos de uma vez

        # --- 4. Área de Log (Terminal no Rodapé) ---
        self.frame_log = ctk.CTkFrame(self, fg_color="gray10", height=100, corner_radius=0)
        self.frame_log.pack(side="bottom", fill="x")
        self.frame_log.pack_propagate(False) # Impede que o frame encolha
        # Terminal estilo "Hacker/Console" (Texto verde no fundo preto)
        self.console_log = ctk.CTkTextbox(self.frame_log, fg_color="#080808", font=("Consolas", 12), text_color="#00FF00")
        self.console_log.pack(fill="both", expand=True, padx=10, pady=5)
        
        # --- 5. Gerenciamento de Telas (Navegação SPA - Single Page Application) ---
        self.frame_telas = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_telas.pack(fill="both", expand=True)
        
        # Cria os containers para cada tela do sistema
        self.tela_menu_inicial = ctk.CTkFrame(self.frame_telas, fg_color="transparent")
        self.tela_slider = ctk.CTkFrame(self.frame_telas, fg_color="transparent")
        self.tela_texto = ctk.CTkFrame(self.frame_telas, fg_color="transparent")
        self.tela_executar = ctk.CTkFrame(self.frame_telas, fg_color="transparent")

        # Constrói o conteúdo de cada tela chamando os métodos específicos
        self.construir_menu_inicial()
        self.construir_tela_slider()
        self.construir_tela_texto()
        self.construir_tela_executar()

        # Ativa os atalhos de teclado globais
        self.configurar_atalhos_teclado()

        # Inicia o software mostrando o menu principal
        self.mostrar_tela(self.tela_menu_inicial)
        self.escrever_log("⚙️ Sistema Robix atualizado. Pressione F1 para o Manual do Operador.")


    # =========================================================================
    # MANUAL DO OPERADOR (AJUDA INDUSTRIAL F1)
    # =========================================================================
    def abrir_ajuda(self, event=None):
        # Se a janela de ajuda já estiver aberta, apenas traz ela para a frente
        if hasattr(self, "janela_ajuda") and self.janela_ajuda.winfo_exists():
            self.janela_ajuda.focus()
            return

        # Cria uma janela secundária flutuante (Toplevel)
        self.janela_ajuda = ctk.CTkToplevel(self)
        self.janela_ajuda.title("Manual do Operador - Robix IFMT")
        self.janela_ajuda.geometry("900x600")
        self.janela_ajuda.configure(fg_color="#1E1E1E")
        self.janela_ajuda.transient(self) # Garante que a janela fique sempre por cima da principal

        # Layout do manual: Índice à esquerda e conteúdo à direita
        frame_esq = ctk.CTkFrame(self.janela_ajuda, width=250, corner_radius=0, fg_color="gray15")
        frame_esq.pack(side="left", fill="y")
        frame_esq.pack_propagate(False)

        frame_dir = ctk.CTkFrame(self.janela_ajuda, fg_color="transparent")
        frame_dir.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame_esq, text="ÍNDICE (F1)", font=("Arial", 16, "bold"), text_color="#569CD6").pack(pady=20)

        self.caixa_texto_ajuda = ctk.CTkTextbox(frame_dir, font=("Arial", 14), wrap="word", fg_color="gray10", text_color="#E0E0E0")
        self.caixa_texto_ajuda.pack(fill="both", expand=True)

        # Dicionário contendo os textos do manual
        textos_manual = {
            "1. Visão Geral & Serial": "O Supervisório Robix é um software HMI...",
            "2. Teach Pendant": "A tela TEACH PENDANT permite o controle manual...",
            "3. Editor (Linguagem)": "O Editor compila a Linguagem Robix...",
            "4. Painel de Execução": "Esta é a interface isolada para o Operador Final...",
            "5. Segurança e Emergência": "A SEGURANÇA FÍSICA E DE HARDWARE É PRIORIDADE..."
        }

        # Função interna que troca o texto exibido quando clica no índice
        def mudar_topico(titulo):
            self.caixa_texto_ajuda.configure(state="normal")
            self.caixa_texto_ajuda.delete("1.0", "end")
            self.caixa_texto_ajuda.insert("1.0", f"--- {titulo.upper()} ---\n\n")
            self.caixa_texto_ajuda.insert("end", textos_manual[titulo])
            self.caixa_texto_ajuda.configure(state="disabled") # Trava para edição

        # Cria os botões do índice dinamicamente
        for titulo in textos_manual.keys():
            btn = ctk.CTkButton(frame_esq, text=titulo, anchor="w", fg_color="transparent", 
                                text_color="white", hover_color="gray25", 
                                command=lambda t=titulo: mudar_topico(t))
            btn.pack(fill="x", padx=10, pady=2)

        mudar_topico("1. Visão Geral & Serial") # Carrega o primeiro tópico por padrão

    # =========================================================================
    # CONTROLE DE ATALHOS DE TECLADO E EMERGÊNCIA
    # =========================================================================
    def configurar_atalhos_teclado(self):
        # A barra de espaço serve como Botão de Emergência Global (STOP)
        self.bind("<space>", self.acao_espaco_emergencia)
        
        # Atalhos de navegação entre as telas do supervisório
        self.bind("<F1>", self.abrir_ajuda) 
        self.bind("<F2>", lambda e: self.mostrar_tela(self.tela_menu_inicial))
        self.bind("<F3>", lambda e: self.mostrar_tela(self.tela_slider))
        self.bind("<F4>", lambda e: self.mostrar_tela(self.tela_texto))
        self.bind("<F5>", lambda e: self.mostrar_tela(self.tela_executar))
        
        # Atalho inteligente para rodar a rotina onde quer que esteja
        self.bind("<F9>", self.rodar_rotina_f9)
        
        # Atalhos do Teach Pendant (Navegar entre motores sem usar o mouse)
        self.bind("<Tab>", lambda e: self.navegar_motores(e, 1))
        self.bind("<Shift-Tab>", lambda e: self.navegar_motores(e, -1))
        self.bind("<Left>", lambda e: self.ajustar_motor_teclado(e, -1))
        self.bind("<Right>", lambda e: self.ajustar_motor_teclado(e, 1))
        self.bind("<Down>", lambda e: self.ajustar_motor_teclado(e, -10))
        self.bind("<Up>", lambda e: self.ajustar_motor_teclado(e, 10))

    def rodar_rotina_f9(self, event=None):
        """Inteligência do F9: Executa o código da aba que estiver aberta."""
        if self.tela_texto.winfo_ismapped():
            self.rodar_f() # Roda do Editor
        elif self.tela_executar.winfo_ismapped():
            self.rodar_execucao() # Roda do Painel Final
        else:
            self.escrever_log("⚠️ Pressione F4 (Editor) ou F5 (Painel) antes de usar o F9 para rodar.", True)

    def acao_espaco_emergencia(self, event):
        # Proteção: Se o usuário estiver digitando no editor de código ou num campo de nome, 
        # a barra de espaço deve funcionar como espaço normal, e não como parada de emergência.
        widget_em_foco = self.focus_get()
        if isinstance(widget_em_foco, (tk.Entry, tk.Text, ctk.CTkTextbox, ctk.CTkEntry)): return
        self.parar_execucao_agora()

    # --- Lógica de navegação do Teach Pendant pelo teclado ---
    def navegar_motores(self, event, direcao):
        if not self.tela_slider.winfo_ismapped(): return
        self.motor_selecionado_idx = (self.motor_selecionado_idx + direcao) % 6
        self.destacar_motor(self.motor_selecionado_idx)
        return "break" # Impede que o TAB pule para outros widgets do sistema

    def destacar_motor(self, idx_selecionado):
        # Coloca uma borda azul no motor selecionado via teclado
        for i, frame in enumerate(self.frames_motores):
            if i == idx_selecionado: frame.configure(border_width=2, border_color="#3a7ebf")
            else: frame.configure(border_width=0)

    def ajustar_motor_teclado(self, event, delta):
        if not self.tela_slider.winfo_ismapped(): return
        self.inc_s(self.motor_selecionado_idx, delta)
        return "break"

    # =========================================================================
    # FUNÇÕES GLOBAIS DE SISTEMA (LOG, NAVEGAÇÃO, SERIAL)
    # =========================================================================
    def escrever_log(self, msg, erro=False):
        """Registra mensagens no console do rodapé com timestamp."""
        ts = time.strftime("%H:%M:%S")
        self.console_log.configure(state="normal")
        # Se for erro, adiciona o emoji ❌
        self.console_log.insert("end", f"[{ts}] {'❌ ' if erro else ''}{msg}\n")
        self.console_log.see("end") # Rola o texto automaticamente para baixo
        self.console_log.configure(state="disabled")

    def mostrar_tela(self, tela_destino):
        """Esconde todas as telas e mostra apenas a selecionada (Navegação)."""
        self.parar_execucao = True # Por segurança, aborta o robô ao trocar de aba
        for t in [self.tela_menu_inicial, self.tela_slider, self.tela_texto, self.tela_executar]: 
            t.place_forget() # Remove da tela
        tela_destino.place(relx=0, rely=0, relwidth=1, relheight=1) # Expande a nova tela

    def criar_toolbar_global(self, parent, titulo, botoes=None):
        """Cria o cabeçalho padrão com o título, botões de tela, porta serial e botões extras."""
        toolbar = ctk.CTkFrame(parent, height=50, fg_color="gray15", corner_radius=0)
        toolbar.pack(side="top", fill="x")
        toolbar.pack_propagate(False)
        
        # Lado Esquerdo: Navegação
        f_esq = ctk.CTkFrame(toolbar, fg_color="transparent")
        f_esq.pack(side="left", fill="y", padx=5)
        
        nav_botoes = [
            ("🏠", self.tela_menu_inicial, "Menu Inicial (F2)"), 
            ("🎮", self.tela_slider, "Teach Pendant (F3)"), 
            ("📝", self.tela_texto, "Editor de Código (F4)"),
            ("🚀", self.tela_executar, "Painel de Execução (F5)")
        ]
        
        for icon, target, hint in nav_botoes:
            btn = ctk.CTkButton(f_esq, text=icon, width=40, height=35, command=lambda t=target: self.mostrar_tela(t))
            btn.pack(side="left", padx=2); ToolTip(btn, hint)
            
        btn_ajuda = ctk.CTkButton(f_esq, text="❓", width=40, height=35, fg_color="#1f538d", command=self.abrir_ajuda)
        btn_ajuda.pack(side="left", padx=10); ToolTip(btn_ajuda, "Manual do Operador (F1)")
        
        # Lado Direito: Controles Seriais e Botões Extras da Tela
        f_dir = ctk.CTkFrame(toolbar, fg_color="transparent")
        f_dir.pack(side="right", fill="y", padx=10)
        
        # Combobox para escolher a porta COM
        cb = ctk.CTkOptionMenu(f_dir, variable=self.porta_selecionada, command=self.conectar_arduino, width=140)
        cb.pack(side="right", padx=5)
        self.lista_combos_portas.append(cb) 
        self.atualizar_lista_portas()

        chk_debug = ctk.CTkCheckBox(f_dir, text="Monitor", variable=self.var_debug_serial, font=("Arial", 12, "bold"))
        chk_debug.pack(side="right", padx=15); ToolTip(chk_debug, "Mostrar pacotes de dados no Log")

        # Adiciona os botões específicos da tela atual (ex: Play, Salvar, Abrir)
        if botoes:
            for item in botoes:
                b = ctk.CTkButton(f_dir, text=item[0], width=40, height=35, command=item[2])
                b.pack(side="right", padx=2); ToolTip(b, item[1])

        # Título centralizado
        ctk.CTkLabel(toolbar, text=titulo, font=("Arial", 16, "bold"), text_color="white").pack(side="left", expand=True, fill="x")

    def conectar_arduino(self, porta):
        if porta == "🔄 Atualizar...": 
            self.atualizar_lista_portas()
            return
        ok, msg = self.porta_serial.conectar(porta)
        self.escrever_log(msg, not ok)

    def atualizar_lista_portas(self):
        # Busca as portas disponíveis no GerenciadorSerial e atualiza todos os dropdowns da interface
        portas = self.porta_serial.listar_portas() + ["🔄 Atualizar..."]
        for combo in self.lista_combos_portas: 
            combo.configure(values=portas)

    def enviar_serial(self, m, a):
        """Valida os limites físicos (Soft Limits) e envia o pacote de dados pela porta USB."""
        if not (1 <= m <= 6 and 0 <= a <= 180): 
            self.escrever_log(f"Limites físicos excedidos: Motor {m}, Angulo {a}°!", True)
            return
            
        # O formato de pacote definido foi <Motor,Angulo>
        if self.porta_serial.enviar(f"<{m},{a}>"):
            if self.var_debug_serial.get(): self.escrever_log(f"📡 [TX] <{m},{a}>")
        else: 
            self.escrever_log("Erro de comunicação Serial!", True)

    def aguardar_com_parada(self, ms):
        """Função de Delay (Wait) customizada. 
        Ela não trava a interface como o time.sleep() faria, e permite abortar no meio do caminho."""
        fim = time.time() + ms / 1000.0
        while time.time() < fim and not self.parar_execucao: 
            self.update()     # Mantém a UI responsiva
            time.sleep(0.02)  # Alivia o uso do processador do PC

    def parar_execucao_agora(self): 
        # Dispara a flag que interrompe o parser de código e as funções de espera
        self.parar_execucao = True
        self.escrever_log("🛑 Parada de emergência ativada.", True)


    # =========================================================================
    # COMPILADOR E INTERPRETADOR DA LINGUAGEM ROBIX
    # =========================================================================
    def processar_codigo(self, texto_codigo):
        """O coração da inteligência de software. Analisa a identação e separa blocos."""
        self.parar_execucao = False
        self.escrever_log("🚀 Compilando código (Análise de Identação)...")
        
        linhas = texto_codigo.split("\n")
        self.metodos_salvos = {}  # Reseta os métodos a cada nova execução
        bloco_setup = []
        bloco_loop = []
        
        estado_alvo = "root" # Define onde a linha lida deve ser armazenada
        nivel_base = -1      # Guarda quantos espaços o bloco principal possui
        
        # 1. PARSER: Lê linha a linha e separa o código em gavetas (setup, loop, metodos)
        for linha_bruta in linhas:
            # Remove comentários (//) e pontos-e-vírgulas residuais
            linha_sem_comentario = linha_bruta.split("//")[0].rstrip().rstrip(';')
            if not linha_sem_comentario.strip(): continue # Pula linhas vazias
            
            # Calcula a identação (número de espaços no início da linha)
            identacao = len(linha_sem_comentario) - len(linha_sem_comentario.lstrip())
            cmd = linha_sem_comentario.strip()
            
            # Encontra declaração de função: "metodo NOME:"
            match_metodo = re.search(r"^metodo\s+([a-zA-Z0-9_]+)\s*:", cmd, re.IGNORECASE)
            if match_metodo:
                nome = match_metodo.group(1)
                self.metodos_salvos[nome] = []
                estado_alvo = f"metodo_{nome}" # Próximas linhas identadas vão para este método
                nivel_base = identacao
                self.escrever_log(f"📦 Método '{nome}' registrado na memória.")
                continue
                
            # Identifica o bloco Setup
            if cmd.lower() == "setup:":
                estado_alvo = "setup_block"
                nivel_base = identacao
                continue
                
            # Identifica o bloco Loop
            if cmd.lower() == "loop:":
                estado_alvo = "loop_block"
                nivel_base = identacao
                continue
                
            # Se a linha atual tem mais espaços que a declaração do bloco, ela pertence a ele
            if nivel_base != -1 and identacao > nivel_base:
                if estado_alvo.startswith("metodo_"):
                    nome = estado_alvo.replace("metodo_", "")
                    self.metodos_salvos[nome].append(cmd)
                elif estado_alvo == "setup_block":
                    bloco_setup.append(cmd)
                elif estado_alvo == "loop_block":
                    bloco_loop.append(cmd)
            else:
                # Se não tem identação, é um comando global solto
                estado_alvo = "root"
                nivel_base = -1
                bloco_setup.append(cmd)

        # 2. EXECUÇÃO: Roda o bloco Setup uma única vez
        if bloco_setup:
            self.escrever_log("▶ Executando bloco SETUP...")
            for cmd in bloco_setup:
                if self.parar_execucao: break
                self.executar_comando(cmd)

        # 3. EXECUÇÃO: Roda o bloco Loop infinitamente (até a parada de emergência)
        if bloco_loop and not self.parar_execucao:
            self.escrever_log("🔄 Executando LOOP contínuo (Pressione ESPAÇO para parar)...")
            while not self.parar_execucao:
                for cmd in bloco_loop:
                    if self.parar_execucao: break
                    self.executar_comando(cmd)

        if not self.parar_execucao:
            self.escrever_log("🏁 Fim da execução.")

    def executar_comando(self, cmd):
        """Interpreta e executa um comando individual. Chama a Serial e atualiza a UI."""
        if self.parar_execucao: return
        self.update() 
        
        # Se for uma chamada a um método criado pelo usuário, entra no método e roda suas linhas
        if cmd in self.metodos_salvos:
            for sub_cmd in self.metodos_salvos[cmd]:
                if self.parar_execucao: break
                self.executar_comando(sub_cmd) # Recursividade
            return
            
        # RegEx para o comando MoveTo(Motor, Angulo)
        m_mov = re.search(r"MoveTo\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)", cmd, re.IGNORECASE)
        if m_mov:
            motor = int(m_mov.group(1))
            angulo = int(m_mov.group(2))
            angulo_atual = int(self.sliders[motor-1].get())
            diferenca = abs(angulo - angulo_atual)
            
            self.enviar_serial(motor, angulo)
            self.sliders[motor-1].set(angulo) # Move o slider visualmente
            
            # Cálculo matemático de tempo de espera baseado no deslocamento mecânico (15ms por grau)
            tempo_espera = (diferenca * 15) + 100
            if diferenca > 0: self.aguardar_com_parada(tempo_espera)
            return

        # RegEx para o comando MovePose (Interpolação dos 6 motores juntos)
        m_pose = re.search(r"MovePose\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", cmd, re.IGNORECASE)
        if m_pose:
            angulos_alvo = [int(m_pose.group(i)) for i in range(1, 7)]
            max_diferenca = 0
            
            for i in range(6):
                angulo_atual = int(self.sliders[i].get())
                diferenca = abs(angulos_alvo[i] - angulo_atual)
                # Encontra qual junta vai fazer o movimento mais longo
                if diferenca > max_diferenca: max_diferenca = diferenca
                    
                self.enviar_serial(i+1, angulos_alvo[i])
                self.sliders[i].set(angulos_alvo[i]) 
            
            # O tempo de espera é baseado no motor que vai demorar mais para chegar
            tempo_espera = (max_diferenca * 15) + 200 
            if max_diferenca > 0: self.aguardar_com_parada(tempo_espera)
            return
            
        # RegEx para o comando Wait(ms)
        m_wait = re.search(r"Wait\s*\(\s*(\d+)\s*\)", cmd, re.IGNORECASE)
        if m_wait:
            self.aguardar_com_parada(int(m_wait.group(1)))
            return
            
        self.escrever_log(f"Sintaxe não reconhecida: '{cmd}'", True)


    # =========================================================================
    # CONSTRUÇÃO DAS INTERFACES GRÁFICAS (Telas Específicas)
    # =========================================================================
    def construir_menu_inicial(self):
        self.criar_toolbar_global(self.tela_menu_inicial, "MENU PRINCIPAL")
        ctk.CTkLabel(self.tela_menu_inicial, text="ROBIX IFMT", font=("Arial", 40, "bold")).pack(expand=True)

    def construir_tela_slider(self):
        self.criar_toolbar_global(self.tela_slider, "TEACH PENDANT", [("⏹", "PARAR ROBÔ (ESPAÇO)", self.parar_execucao_agora)])
        
        rol = ctk.CTkScrollableFrame(self.tela_slider, fg_color="transparent")
        rol.pack(fill="both", expand=True)
        
        # Painel de controle superior do Teach Pendant
        ctrl = ctk.CTkFrame(rol, fg_color="gray20", corner_radius=10)
        ctrl.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkSwitch(ctrl, text="Modo Tempo Real", variable=self.var_tempo_real).pack(side="left", padx=20, pady=15)
        ctk.CTkButton(ctrl, text="▶ Enviar Pose", fg_color="#1f538d", command=self.enviar_pose_offline).pack(side="left", padx=10)
        
        self.btn_salvar = ctk.CTkButton(ctrl, text="📌 Salvar Ponto", fg_color="#28a745", command=self.salvar_pose)
        self.btn_salvar.pack(side="left", padx=10)
        
        self.entry_nome_rotina = ctk.CTkEntry(ctrl, placeholder_text="Nome da Rotina", width=140)
        self.entry_nome_rotina.pack(side="right", padx=(10, 20))
        
        ctk.CTkButton(ctrl, text="📝 Exportar", command=self.exportar).pack(side="right", padx=10)

        # Grid para posicionar os 6 sliders
        grid = ctk.CTkFrame(rol, fg_color="transparent")
        grid.pack(expand=True, pady=10)
        
        nomes = ["Base", "Ombro", "Cotovelo", "Pitch", "Roll", "Garra"]
        self.sliders = []
        self.labels = []
        
        # Cria os 6 blocos de controle de junta dinamicamente
        for i in range(6):
            f = ctk.CTkFrame(grid, width=320, height=140, corner_radius=10)
            f.grid(row=i//2, column=i%2, padx=10, pady=10)
            f.grid_propagate(False)
            self.frames_motores.append(f)
            
            ctk.CTkLabel(f, text=f"{i+1}. {nomes[i]}", font=("Arial", 12, "bold")).place(x=15, y=10)
            lbl_valor = ctk.CTkLabel(f, text="90°", text_color="#1f538d", font=("Arial", 14, "bold"))
            lbl_valor.place(x=260, y=10)
            self.labels.append(lbl_valor)
            
            # Quando arrasta o slider, chama mover_s. Quando solta o clique, chama final_s.
            slider = ctk.CTkSlider(f, from_=0, to=180, command=lambda v, idx=i: self.mover_s(idx, v))
            slider.set(90)
            slider.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8)
            slider.bind("<ButtonRelease-1>", lambda e, idx=i: self.final_s(idx))
            self.sliders.append(slider)
            
            # Botões de ajuste fino (+1, -1, +10, -10)
            fb = ctk.CTkFrame(f, fg_color="transparent")
            fb.place(relx=0.5, rely=0.85, anchor="center")
            for d in [-10, -1, 1, 10]:
                ctk.CTkButton(fb, text=f"{'+' if d>0 else ''}{d}", width=45, height=25, 
                              command=lambda idx=i, delta=d: self.inc_s(idx, delta)).pack(side="left", padx=2)

        self.destacar_motor(0) # Inicializa destacando a base

    # Lógicas de interação dos Sliders do Teach Pendant
    def enviar_pose_offline(self):
        self.escrever_log("▶ Sincronizando robô com a pose atual...")
        for i, s in enumerate(self.sliders): self.enviar_serial(i+1, int(s.get()))

    def mover_s(self, i, v):
        """Atualiza a label durante o arraste e envia serial SE estiver em Tempo Real e houver gap de tempo."""
        self.labels[i].configure(text=f"{int(v)}°")
        if self.var_tempo_real.get() and time.time() - self.tempos_motores[i] > 0.05:
            self.enviar_serial(i+1, int(v))
            self.tempos_motores[i] = time.time()

    def final_s(self, i):
        """Garante o envio da posição exata final ao soltar o mouse (Tempo Real)."""
        if self.var_tempo_real.get(): self.enviar_serial(i+1, int(self.sliders[i].get()))

    def inc_s(self, i, d):
        """Lógica dos botões de ajuste fino (+1, -1) ou setas do teclado."""
        nv = max(0, min(180, int(self.sliders[i].get()) + d))
        self.sliders[i].set(nv)
        self.mover_s(i, nv)
        self.final_s(i)

    # Lógica de Gravação e Exportação de Pontos
    def salvar_pose(self):
        """Lê os 6 ângulos atuais e formata numa string MovePose para guardar na lista."""
        p = f"MovePose({', '.join([str(int(s.get())) for s in self.sliders])})\n"
        self.rotina_gravada.append(p)
        
        self.escrever_log(f"📍 Ponto {len(self.rotina_gravada)} salvo na memória.")
        self.btn_salvar.configure(text="✅ Salvo!", fg_color="#155724")
        self.after(1000, lambda: self.btn_salvar.configure(text="📌 Salvar Ponto", fg_color="#28a745"))

    def exportar(self):
        """Transforma a lista de pontos gravados em um código robusto, com metodos, setup e loop."""
        if not self.rotina_gravada: return
        
        nome = self.entry_nome_rotina.get().strip()
        nome_metodo = nome if nome else "RotinaGravada"
        
        # Constrói o código string aplicando recuos (identação) corretamente
        codigo = f"metodo {nome_metodo}:\n"
        for i, pose in enumerate(self.rotina_gravada):
            codigo += f"    // Ponto {i+1}\n"
            codigo += f"    {pose}"
            codigo += f"    Wait(1000)\n" # Insere delay automático entre as poses
            
        codigo += "\nsetup:\n"
        codigo += f"    // Posição de repouso (Ponto inicial)\n"
        codigo += f"    {self.rotina_gravada[0]}"
        
        codigo += "\nloop:\n"
        codigo += f"    // Executa a rotina infinitamente\n"
        codigo += f"    {nome_metodo}\n"
        
        # Muda para a tela do Editor e joga o código gerado lá dentro
        self.mostrar_tela(self.tela_texto)
        self.caixa_texto_programacao.delete("1.0", "end")
        self.caixa_texto_programacao.insert("1.0", codigo)
        
        # Limpa os dados do gerador
        self.rotina_gravada = []
        self.entry_nome_rotina.delete(0, "end")
        self.escrever_log(f"📝 Template '{nome_metodo}' gerado com sucesso!")

    # =========================================================================
    # TELAS DO EDITOR E EXECUÇÃO FINAL
    # =========================================================================
    def construir_tela_texto(self):
        acoes = [
            ("📂", "Abrir Arquivo", self.abrir_f), 
            ("💾", "Salvar Arquivo", self.salvar_f), 
            ("▶", "Rodar Rotina (F9)", self.rodar_f), 
            ("⏹", "STOP", self.parar_execucao_agora)
        ]
        self.criar_toolbar_global(self.tela_texto, "EDITOR DE CÓDIGO", acoes)
        
        f_ed = ctk.CTkFrame(self.tela_texto, fg_color="transparent")
        f_ed.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Instancia o módulo EditorComLinhas criado anteriormente
        self.caixa_texto_programacao = EditorComLinhas(f_ed)
        self.caixa_texto_programacao.pack(side="left", fill="both", expand=True)
        # Instancia o módulo visual DicionarioComandos à direita
        DicionarioComandos(f_ed, width=300).pack(side="right", fill="y", padx=(10, 0))

    def rodar_f(self):
        # Extrai o texto do editor e manda para o interpretador
        codigo = self.caixa_texto_programacao.get("1.0", "end-1c")
        self.processar_codigo(codigo)

    def abrir_f(self):
        p = filedialog.askopenfilename(filetypes=[("TXT", "*.txt")])
        if p:
            with open(p, 'r') as f:
                self.caixa_texto_programacao.delete("1.0", "end")
                self.caixa_texto_programacao.insert("1.0", f.read())
            self.escrever_log(f"📂 Aberto: {os.path.basename(p)}")

    def salvar_f(self):
        p = filedialog.asksaveasfilename(defaultextension=".txt")
        if p:
            with open(p, 'w') as f: 
                f.write(self.caixa_texto_programacao.get("1.0", "end-1c"))
            self.escrever_log("💾 Rotina salva com sucesso.")

    def construir_tela_executar(self):
        acoes = [
            ("📂", "Carregar Arquivo", self.abrir_execucao), 
            ("▶", "Iniciar (F9)", self.rodar_execucao), 
            ("⏹", "STOP", self.parar_execucao_agora)
        ]
        self.criar_toolbar_global(self.tela_executar, "PAINEL DE EXECUÇÃO", acoes)
        
        # Reutiliza o visualizador de código, mas trava ele para não permitir edição (Segurança)
        self.caixa_visualizacao = EditorComLinhas(self.tela_executar)
        self.caixa_visualizacao.configure(state="disabled")
        self.caixa_visualizacao.pack(fill="both", expand=True, padx=20, pady=20)

    def abrir_execucao(self):
        p = filedialog.askopenfilename(filetypes=[("TXT", "*.txt")])
        if p:
            with open(p, 'r') as f:
                # Destrava rapidamente só para injetar o texto, e trava de novo
                self.caixa_visualizacao.configure(state="normal")
                self.caixa_visualizacao.delete("1.0", "end")
                self.caixa_visualizacao.insert("1.0", f.read())
                self.caixa_visualizacao.configure(state="disabled")
            self.escrever_log(f"📂 Arquivo carregado: {os.path.basename(p)}")

    def rodar_execucao(self):
        codigo = self.caixa_visualizacao.get("1.0", "end-1c")
        self.processar_codigo(codigo)
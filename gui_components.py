import customtkinter as ctk
import tkinter as tk
import re  # Biblioteca para Expressões Regulares (usada para buscas complexas de texto e colorização)

# ==========================================
# CLASSE TOOLTIP (DICAS FLUTUANTES)
# ==========================================
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget  # O elemento (ex: botão) que vai disparar a dica
        self.text = text      # O texto que vai aparecer na dica
        self.tip_window = None # Variável que vai guardar a janela da dica
        
        # Cria "ouvintes" para quando o mouse entra e sai de cima do elemento
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        # Se a janela já existe ou se não há texto, não faz nada
        if self.tip_window or not self.text: return
        
        # Calcula as coordenadas X e Y para a dica aparecer perto do mouse/widget
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        # Cria uma nova janela "flutuante" (Toplevel) anexada ao widget original
        self.tip_window = tk.Toplevel(self.widget)
        # Remove as bordas padrão do Windows/Mac/Linux da janelinha
        self.tip_window.wm_overrideredirect(True)
        # Define a posição da janela na tela
        self.tip_window.wm_geometry(f"+{x}+{y}")
        
        # Adiciona o texto dentro da janelinha flutuante com cores e bordas estilizadas
        tk.Label(self.tip_window, text=self.text, background="#333333", fg="white", 
                 relief="solid", borderwidth=1, font=("Arial", 11)).pack(ipadx=5, ipady=2)

    def hide_tip(self, event=None):
        # Se o mouse saiu e a janela da dica existe, nós a destruímos
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


# ==========================================
# CLASSE EDITOR DE CÓDIGO COM LINHAS
# ==========================================
class EditorComLinhas(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Configura o layout: coluna 0 (números) é fixa, coluna 1 (editor) expande
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # 1. Caixa de Números das Linhas (Usando tk.Text padrão)
        # Fica desabilitada (state="disabled") para o usuário não digitar nela
        self.caixa_linhas = tk.Text(self, width=4, bg="#1a1a1a", fg="#666666", 
                                    font=("Consolas", 14), state="disabled", 
                                    borderwidth=0, highlightthickness=0, pady=7)
        self.caixa_linhas.grid(row=0, column=0, sticky="ns", padx=(5, 0))
        
        # 2. Caixa de Texto Principal (Onde o código é digitado)
        self.caixa_texto = ctk.CTkTextbox(self, font=("Consolas", 14), wrap="none")
        self.caixa_texto.grid(row=0, column=1, sticky="nsew")
        
        # Ativa o histórico de "Desfazer" (Ctrl+Z) na caixa de texto
        self.caixa_texto._textbox.configure(undo=True, autoseparators=True, maxundo=-1)
        
        # Palavras-chave nativas do seu robô para o autocompletar
        self.palavras_chave = ["MoveTo()", "MovePose()", "Wait()", "metodo ", "setup:", "loop:"]

        # 3. Configuração de Atalhos de Teclado (Bindings)
        self.caixa_texto.bind("<Tab>", self.autocompletar_ou_identar)
        self.caixa_texto.bind("<Return>", self.auto_identar_enter)
        self.caixa_texto.bind("<BackSpace>", self.smart_backspace)

        # Eventos que exigem que a tela seja atualizada (cores e números de linhas)
        eventos = ["<KeyRelease>", "<MouseWheel>", "<Control-v>", "<Control-z>"]
        for ev in eventos:
            self.caixa_texto.bind(ev, self.processar_eventos)
            
        # 4. Sincronização de Rolagem (Scroll)
        # Intercepta a barra de rolagem do texto principal para rolar os números junto
        self._orig_yscroll = self.caixa_texto._textbox.cget("yscrollcommand")
        self.caixa_texto._textbox.configure(yscrollcommand=self._sync_scroll)
        
        # Atualiza a interface pela primeira vez
        self._atualizar_numeros()
        self.configurar_cores()

    def smart_backspace(self, event):
        # Apaga blocos de espaços (identação) de uma vez só no início da linha
        txt = self.caixa_texto._textbox
        pos_atual = txt.index("insert") # Posição do cursor
        linha, col = pos_atual.split(".")
        col = int(col)
        
        if col > 0:
            texto_antes = txt.get(f"{linha}.0", pos_atual)
            # Se só tem espaços antes do cursor, apaga tudo
            if texto_antes.isspace() and len(texto_antes) == col:
                txt.delete(f"{linha}.0", pos_atual)
                self.processar_eventos()
                return "break" # Impede o comportamento padrão do backspace
        self.processar_eventos()

    def auto_identar_enter(self, event):
        # Mantém o mesmo nível de recuo (espaços) quando o usuário aperta Enter
        txt = self.caixa_texto._textbox
        pos_atual = txt.index("insert")
        linha = pos_atual.split(".")[0]
        texto_linha = txt.get(f"{linha}.0", f"{linha}.end")
        
        # Pega todos os espaços no começo da linha atual
        match_espacos = re.match(r"^(\s*)", texto_linha)
        espacos = match_espacos.group(1) if match_espacos else ""
        
        # Insere a quebra de linha (\n) seguida dos espaços
        txt.insert("insert", "\n" + espacos)
        self.processar_eventos()
        return "break" 

    def autocompletar_ou_identar(self, event):
        # Lógica inteligente para o TAB: autocompleta comandos ou insere espaços
        txt = self.caixa_texto._textbox
        pos_atual = txt.index("insert")
        linha = pos_atual.split(".")[0]
        texto_linha = txt.get(f"{linha}.0", pos_atual)
        
        # Busca a palavra que o usuário está digitando (antes do cursor)
        match = re.search(r'([a-zA-Z_0-9]+[\(]*)$', texto_linha)
        if match:
            palavra_atual_raw = match.group(1)
            palavra_limpa = palavra_atual_raw.replace("(", "")
            
            # Lê o texto todo para encontrar métodos customizados pelo usuário
            texto_completo = txt.get("1.0", "end")
            nomes_metodos = []
            for m in re.finditer(r"metodo\s+([a-zA-Z0-9_]+)\s*:", texto_completo, re.IGNORECASE):
                nomes_metodos.append(m.group(1))
                
            # Junta as palavras do sistema com os métodos do usuário
            todas_palavras = self.palavras_chave + nomes_metodos

            # Lógica para alternar entre sugestões se apertar TAB várias vezes
            sugestoes_limpas = [s.replace("()", "") for s in getattr(self, '_sugestoes_atuais', [])]
            if hasattr(self, '_sugestoes_atuais') and palavra_limpa in sugestoes_limpas:
                self._indice_sugestao = (self._indice_sugestao + 1) % len(self._sugestoes_atuais)
                sugestao = self._sugestoes_atuais[self._indice_sugestao]

                # Substitui o texto digitado pela sugestão
                inicio_palavra = f"{pos_atual} - {len(palavra_atual_raw)} chars"
                txt.delete(inicio_palavra, pos_atual)
                if txt.get("insert", "insert+1c") == ")":
                    txt.delete("insert", "insert+1c")
                txt.insert("insert", sugestao)
                if sugestao.endswith("()"):
                    txt.mark_set("insert", "insert-1c") # Posiciona o cursor dentro dos parênteses
                self.processar_eventos()
                return "break"

            # Se for a primeira vez apertando TAB, busca as opções que começam com o texto digitado
            sugestoes = [p for p in todas_palavras if p.lower().startswith(palavra_limpa.lower())]
            
            if sugestoes:
                self._sugestoes_atuais = sugestoes
                self._indice_sugestao = 0
                sugestao = sugestoes[0]
                
                inicio_palavra = f"{pos_atual} - {len(palavra_atual_raw)} chars"
                txt.delete(inicio_palavra, pos_atual)
                
                if txt.get("insert", "insert+1c") == ")":
                    txt.delete("insert", "insert+1c")
                    
                txt.insert("insert", sugestao)
                
                if sugestao.endswith("()"):
                    txt.mark_set("insert", "insert-1c")
                    
                self.processar_eventos()
                return "break"

        # Se não achou nenhuma palavra para completar, insere 4 espaços (identação padrão)
        if hasattr(self, '_sugestoes_atuais'):
            self._sugestoes_atuais = []

        txt.insert("insert", "    ")
        self.processar_eventos()
        return "break"

    def configurar_cores(self):
        # Define os estilos de texto (tags) para o Syntax Highlighting (Colorização)
        txt = self.caixa_texto._textbox
        txt.tag_config("comando", foreground="#569CD6", font=("Consolas", 14, "bold"))  # Azul claro
        txt.tag_config("numero", foreground="#B5CEA8")                                  # Verde claro
        txt.tag_config("comentario", foreground="#6A9955", font=("Consolas", 14, "italic")) # Verde escuro
        txt.tag_config("estrutura", foreground="#C586C0", font=("Consolas", 14, "bold")) # Roxo
        txt.tag_config("funcao", foreground="#DCDCAA", font=("Consolas", 14))           # Amarelo

    def processar_eventos(self, event=None):
        # Agenda as atualizações visuais com um pequeno atraso (milissegundos)
        # Isso garante que o Tkinter registre a tecla antes de pintarmos o texto
        self.after(1, self._atualizar_numeros)
        self.after(2, self.colorir_sintaxe)

    def colorir_sintaxe(self):
        # Varre o texto e aplica as cores com base em padrões de Expressão Regular (Regex)
        txt = self.caixa_texto._textbox
        texto_completo = txt.get("1.0", "end")
        
        # 1. Limpa todas as cores atuais
        for tag in ["comando", "numero", "comentario", "estrutura", "funcao"]:
            txt.tag_remove(tag, "1.0", "end")

        # 2. Encontra e pinta comandos nativos
        for match in re.finditer(r"\b(MoveTo|Wait|MovePose)\b", texto_completo):
            txt.tag_add("comando", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")
            
        # 3. Encontra e pinta blocos de estrutura
        for match in re.finditer(r"\b(metodo|setup:|loop:)\b", texto_completo):
            txt.tag_add("estrutura", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")
            
        # 4. Encontra e pinta números (ex: 180, 500)
        for match in re.finditer(r"\b\d+\b", texto_completo):
            txt.tag_add("numero", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")
            
        # 5. Encontra e pinta comentários (tudo que vier depois de //)
        for match in re.finditer(r"//.*", texto_completo):
            txt.tag_add("comentario", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

        # 6. Encontra e pinta métodos customizados criados pelo usuário
        nomes_metodos = []
        for match in re.finditer(r"metodo\s+([a-zA-Z0-9_]+)\s*:", texto_completo, re.IGNORECASE):
            txt.tag_add("funcao", f"1.0 + {match.start(1)} chars", f"1.0 + {match.end(1)} chars")
            nomes_metodos.append(match.group(1))

        # Se houver métodos, procura onde eles foram chamados no código para pintar também
        if nomes_metodos:
            nomes_metodos.sort(key=len, reverse=True) # Evita bugs com nomes parecidos
            padrao = r"\b(" + "|".join(re.escape(n) for n in nomes_metodos) + r")\b"
            for match in re.finditer(padrao, texto_completo):
                txt.tag_add("funcao", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

    def _sync_scroll(self, *args):
        # Aplica o movimento da barra de rolagem tanto na caixa de texto quanto na de linhas
        if self._orig_yscroll: self.tk.call(self._orig_yscroll, *args)
        self.caixa_linhas.yview_moveto(args[0])

    def _atualizar_numeros(self):
        # Conta as linhas atuais e atualiza a coluna da esquerda com "1, 2, 3..."
        qtd = int(self.caixa_texto.index("end-1c").split(".")[0])
        self.caixa_linhas.configure(state="normal") # Libera para edição via código
        self.caixa_linhas.delete("1.0", "end")
        self.caixa_linhas.insert("1.0", "\n".join(str(i) for i in range(1, qtd + 1)))
        self.caixa_linhas.configure(state="disabled") # Bloqueia novamente
        self.caixa_linhas.yview_moveto(self.caixa_texto._textbox.yview()[0]) # Sincroniza a posição visual
        
    # --- Funções "Envelopadas" (Wrappers) ---
    # Permitem interagir com o EditorComLinhas usando os mesmos comandos de um textbox normal
    def get(self, *args, **kwargs): return self.caixa_texto.get(*args, **kwargs)
    def insert(self, *args, **kwargs): self.caixa_texto.insert(*args, **kwargs); self.processar_eventos()
    def delete(self, *args, **kwargs): self.caixa_texto.delete(*args, **kwargs); self.processar_eventos()
    def index(self, *args, **kwargs): return self.caixa_texto.index(*args, **kwargs)
    def configure(self, **kwargs):
        if "state" in kwargs: self.caixa_texto.configure(state=kwargs["state"])
        else: super().configure(**kwargs)


# ==========================================
# CLASSE DICIONÁRIO DE COMANDOS (MENU LATERAL)
# ==========================================
class DicionarioComandos(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # Visual do painel de dicionário
        self.configure(fg_color="gray15", corner_radius=10)
        
        # Título do painel
        ctk.CTkLabel(self, text="📖 SINTAXE ROBIX", font=("Arial", 11, "bold"), text_color="#1f538d").pack(pady=10)
        
        # Lista de comandos e suas descrições
        cmds = [
            ("MoveTo(M, A)", "M:1-6 | A:0-180"),
            ("MovePose(...)", "B, O, C, P, R, G"),
            ("Wait(MS)", "Pausa em ms"), 
            ("setup:\n    // Roda uma vez", "Configuração Inicial"),
            ("loop:\n    // Roda infinito", "Laço Principal"),
            ("metodo NOME:\n    // Comandos", "Função Customizada"),
            ("// Comentário", "Ignorado pelo robô")
        ]
        
        # Cria visualmente a lista de comandos na interface iterando sobre a lista 'cmds'
        for c, d in cmds:
            f = ctk.CTkFrame(self, fg_color="transparent") # Cria uma linha invisível
            f.pack(fill="x", padx=10, pady=3)
            
            # Mostra o código (Ex: MoveTo) em amarelo
            ctk.CTkLabel(f, text=c, font=("Consolas", 10, "bold"), text_color="yellow", justify="left").pack(anchor="w")
            
            # Mostra a explicação (Ex: M:1-6) em cinza logo abaixo
            ctk.CTkLabel(f, text=d, font=("Arial", 9), text_color="gray70", justify="left").pack(anchor="w")
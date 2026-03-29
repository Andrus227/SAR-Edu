# Importa a biblioteca CustomTkinter e dá a ela o apelido 'ctk' para encurtar o código
import customtkinter as ctk

# Importa a classe principal da sua interface (RobixSupervisorio) que está no arquivo app.py
from app import RobixSupervisorio

# Trava de segurança: garante que este bloco só rode se o arquivo for executado diretamente
if __name__ == "__main__":
    
    # Define o visual do aplicativo para o Modo Escuro (fundo escuro)
    ctk.set_appearance_mode("Dark")
    
    # Define a cor de destaque (botões, seleções, barras) como azul
    ctk.set_default_color_theme("blue")
    
    # Cria a janela principal do aplicativo baseada na classe que importamos
    app = RobixSupervisorio()
    
    # Inicia o "loop infinito" que mantém a janela aberta na tela e responde aos cliques
    app.mainloop()
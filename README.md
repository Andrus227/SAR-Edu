# SAR-Edu: Sistema de Apoio Robótico Educacional com Robix + Arduino Mega

Projeto desenvolvido na disciplina de Robótica Industrial, orientada pelo Prof. Dr. Ronan Marcelo Martins, com foco em controle de um braço robótico do kit Robix via software próprio em Python.

## Objetivo

Desenvolver uma interface para controle de servomotores do braço robótico, visando uso didático em laboratório, com alternativa ao software original do kit Robix.

## Funcionalidades principais

- Controle em tempo real por sliders;
- Envio de poses individuais;
- Gravação de poses ensinadas;
- Geração e execução de rotinas (mini compilador);
- Salvamento de rotinas em arquivo `.txt`;
- Comunicação serial com Arduino Mega.

## Arquitetura (resumo)

- **Python (desktop):**
  - `main.py`
  - `app.py`
  - `gui_components.py`
  - `serial_manager.py`
- **Firmware Arduino:**
  - `Servo/Servo.ino`
- **Comunicação:**
  - Porta serial (notebook → Arduino Mega)

## Experimento realizado

Foi implementada e validada uma rotina de **pick-and-place**, em que o braço:
1. pega um objeto em uma posição inicial;
2. transporta para outra posição;
3. retorna o objeto à posição original.

A tarefa foi executada com sucesso em laboratório.

## Requisitos

- Python 3.x
- Arduino IDE (para upload de `Servo/Servo.ino`)
- Arduino Mega
- Kit Robix com servomotores
- Cabo USB

## Execução (exemplo)

1. Carregue o firmware do Arduino em `Servo/Servo.ino`.
2. Conecte o Arduino Mega ao notebook.
3. Execute o software Python:
   ```bash
   python main.py
   ```
4. Selecione a porta serial correta e inicie o controle.

## Estrutura sugerida para evolução

- `images/` → fotos do protótipo e interface
- `results/` → logs e resultados de testes
- `article/` → rascunho do artigo para submissão

## Autores

- Andrus227 e equipe da disciplina de Robótica Industrial.

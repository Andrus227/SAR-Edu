# Desenvolvimento de um Supervisório Educacional para Braço Robótico Robix com Arduino Mega e Python

## Resumo

Este trabalho apresenta o desenvolvimento de um supervisório educacional para controle de um braço robótico do kit Robix, utilizando Python para interface de usuário e Arduino Mega para acionamento dos servomotores. A proposta surgiu em disciplina de Robótica Industrial diante de limitações práticas do software original do kit em ambiente de laboratório. O sistema implementado permite controle em tempo real por sliders, envio de poses individuais, gravação de poses e execução de rotinas por meio de um interpretador de comandos, com persistência em arquivos texto. Para validação, foi executado um experimento de pick-and-place em bancada, no qual o manipulador realizou com sucesso a movimentação e o retorno de um objeto entre posições pré-definidas. Os resultados indicam viabilidade da solução como ferramenta didática de apoio ao ensino de programação e operação de manipuladores robóticos em contexto educacional.

## 1. Introdução

A robótica educacional e industrial demanda ferramentas de software confiáveis para experimentação prática em laboratório. Em contextos acadêmicos, limitações de compatibilidade, desempenho e manutenção de softwares proprietários podem comprometer atividades didáticas, reduzindo a autonomia dos estudantes e a efetividade das aulas práticas.

Na disciplina de Robótica Industrial, foi proposta a criação de uma alternativa de controle para um braço robótico do kit Robix, com foco em uso educacional. A motivação principal foi contornar dificuldades de instalação e execução do software original em máquinas do laboratório, além de permitir maior flexibilidade para desenvolvimento e testes em equipamentos pessoais dos alunos.

Como resposta a esse problema, foi desenvolvido o SAR-Edu (Supervisório de Automação Robótica Educacional), uma aplicação em Python que se comunica via porta serial com um Arduino Mega responsável pelo acionamento dos servomotores do manipulador. A solução oferece duas formas de operação: (i) controle manual em tempo real por meio de sliders e (ii) programação por poses, com possibilidade de gravação e reutilização de rotinas.

Para verificar a aplicabilidade da solução, foi realizado um experimento de pick-and-place em laboratório. O braço executou as etapas de coleta, transporte e retorno do objeto em posições previamente definidas, demonstrando o potencial do sistema como recurso de apoio ao ensino de robótica e automação.

## 2. Objetivos

### 2.1 Objetivo Geral

Desenvolver e validar um supervisório educacional para controle de braço robótico Robix com servomotores, utilizando Python e comunicação serial com Arduino Mega, visando suporte didático em aulas práticas de Robótica Industrial.

### 2.2 Objetivos Específicos

- Implementar interface gráfica para controle em tempo real das juntas do manipulador;
- Permitir envio de poses individuais e gravação de sequências de poses;
- Implementar mecanismo de execução de rotinas programadas e salvamento em arquivo `.txt`;
- Integrar aplicação desktop em Python ao controlador físico via comunicação serial;
- Avaliar o funcionamento do sistema em experimento de pick-and-place em laboratório;
- Identificar limitações da solução e oportunidades de melhoria para uso acadêmico contínuo.

## 3. Metodologia

A metodologia adotada foi de desenvolvimento aplicado com validação experimental em bancada de laboratório, dividida em quatro etapas: (i) levantamento de requisitos didáticos e técnicos, (ii) implementação do supervisório em Python, (iii) integração com o controlador físico baseado em Arduino Mega e (iv) execução de experimento de validação funcional.

### 3.1 Ambiente e materiais

- Kit de braço robótico Robix com servomotores;
- Arduino Mega;
- Placa de acionamento montada em laboratório;
- Notebook com sistema operacional Windows;
- Aplicação desktop desenvolvida em Python;
- Comunicação serial USB entre notebook e Arduino.

### 3.2 Arquitetura de software

A aplicação foi estruturada em módulos para separação de responsabilidades:

- `main.py`: inicialização da aplicação;
- `app.py`: fluxo principal e orquestração da interface;
- `gui_components.py`: elementos da interface (sliders, comandos de pose e rotinas);
- `serial_manager.py`: gerenciamento da conexão serial e envio de comandos;
- `Servo/Servo.ino`: firmware embarcado no Arduino para interpretação dos comandos e acionamento dos servomotores.

Essa organização favorece manutenção, testes incrementais e reuso em futuras disciplinas.

### 3.3 Estratégia de controle

O sistema oferece dois modos principais de operação:

1. **Controle em tempo real** por sliders, permitindo ajuste direto das juntas;
2. **Programação por poses**, permitindo registrar posições sequenciais e transformá-las em rotinas executáveis.

As rotinas podem ser persistidas em arquivo texto (`.txt`) para reutilização em atividades práticas posteriores.

### 3.4 Procedimento experimental

Para validação funcional, foi executada uma rotina de pick-and-place com três fases:

1. deslocamento até a posição de coleta;
2. transporte do objeto para posição de destino;
3. retorno do objeto para a posição inicial.

A rotina foi ensinada ao sistema por poses sequenciais, armazenada e reexecutada em bancada. A validação considerou sucesso da tarefa, estabilidade do movimento e repetibilidade básica observacional entre execuções.

## 4. Resultados e Discussão

O supervisório desenvolvido foi capaz de estabelecer comunicação serial estável com o Arduino Mega e controlar os servomotores do braço robótico conforme os comandos emitidos pela interface. O modo de controle em tempo real por sliders permitiu ajuste intuitivo das juntas, contribuindo para compreensão dos limites de movimento e da coordenação entre eixos.

No modo de programação por poses, foi possível registrar sequências de posições, armazená-las em arquivo texto e reexecutá-las em laboratório. A rotina de pick-and-place foi concluída com sucesso, evidenciando a viabilidade do sistema para tarefas didáticas de manipulação.

Do ponto de vista pedagógico, a solução apresentou vantagens sobre o cenário inicial, ao reduzir dependência do software original do kit e permitir experimentação em equipamentos dos estudantes. Além disso, a arquitetura modular em Python facilitou a depuração e evolução do sistema durante o semestre.

Como limitações, destacam-se: ausência de planejamento cinemático avançado, dependência de calibração manual para determinadas poses e inexistência de módulo de prevenção automática de colisões. Essas limitações, no entanto, não inviabilizam o uso educacional proposto para práticas introdutórias.

## 5. Considerações Finais

Este trabalho apresentou o desenvolvimento e validação de um supervisório educacional para braço robótico Robix, integrando interface em Python e controle físico via Arduino Mega por comunicação serial. A solução atendeu ao objetivo de apoiar aulas práticas de Robótica Industrial, oferecendo controle manual em tempo real e execução de rotinas programadas por poses.

A validação por experimento pick-and-place demonstrou funcionamento satisfatório em laboratório e potencial de aplicação em atividades de ensino. Como trabalhos futuros, sugere-se: (i) inclusão de módulo de calibração automatizada, (ii) implementação de verificações de limites e colisões, (iii) incorporação de métricas quantitativas de desempenho (tempo de ciclo, erro de repetição e taxa de sucesso) e (iv) evolução para integração com bibliotecas de cinemática e planejamento de trajetória.

## Referências (provisório)

> Inserir referências conforme template e normas do evento de submissão (SBSC/CSBC 2026).

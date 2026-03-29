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
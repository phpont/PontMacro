# PontMacro

## Descrição
PontMacro é um aplicativo de gravação de macros que permite aos usuários gravar e reproduzir ações do mouse. Ideal para automatizar tarefas repetitivas, o aplicativo oferece uma interface amigável e fácil de usar, desenvolvida com PyQt5 e outras bibliotecas Python.

## Funcionalidades
- **Gravação de Macros**: Permite gravar sequências de ações do mouse.
- **Reprodução de Macros**: Reproduz as ações gravadas.
- **Salvar/Carregar Macros**: Os usuários podem salvar suas macros em arquivos e carregá-las conforme necessário.
- **Interface Gráfica do Usuário (GUI)**: Uma GUI limpa e intuitiva construída com PyQt5.
- **Tema Escuro**: Aplicativo com tema escuro utilizando a biblioteca qdarkstyle.

## Requisitos
- Python 3.x
- PyQt5
- pyautogui
- pynput
- qdarkstyle

## Instalação
Para instalar as dependências necessárias, execute o seguinte comando:
pip install PyQt5 pyautogui pynput qdarkstyle


## Execução
Para executar o PontMacro, clone o repositório e execute o arquivo principal:

python pontmacro.py


## Estrutura do Código
- `PontMacroApp`: Classe principal do aplicativo, cria a interface do usuário e gerencia eventos.
- `MacroRecorder`: Classe para gravação de ações do mouse.
- `EventManager`: Classe para gerenciar eventos gravados.
- `EventType`: Enumeração para tipos de eventos (atualmente suporta apenas cliques do mouse).

## Contribuições
Contribuições são bem-vindas. Para contribuir, faça um fork do projeto, crie uma branch para suas alterações e submeta um pull request.



import logging
import pickle
import sys
from enum import Enum

import pyautogui
import qdarkstyle
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QWidget,
    QLabel,
    QFileDialog,
    QProgressBar, QGridLayout,
)
from pynput.mouse import Listener as MouseListener


class EventType(Enum):
    MOUSE_CLICK = 1


class EventManager:
    def __init__(self):
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

    def edit_event(self, index, new_event):
        if 0 <= index < len(self.events):
            self.events[index] = new_event
            return True
        return False

    def delete_event(self, index):
        if 0 <= index < len(self.events):
            del self.events[index]
            return True
        return False

    def clear_events(self):
        self.events.clear()

    def get_events(self):
        return self.events


class MacroRecorder(QThread):
    update_signal = pyqtSignal(str, int)

    def __init__(self, event_manager):
        super().__init__()
        self.recording = False
        self.event_manager = event_manager
        self.listener = MouseListener(on_click=self.on_click)
        self.logger = logging.getLogger("MacroRecorder")
        self.event_count = 0

    def on_click(self, x, y, button, pressed):
        if self.recording:
            event_data = (EventType.MOUSE_CLICK, (x, y, button, pressed))
            self.event_manager.add_event(*event_data)
            self.update_signal.emit(
                f"Clique do mouse capturado: {x}, {y}, {button}, {'pressionado' if pressed else 'solto'}",
                len(self.event_manager.get_events()))

    def run(self):
        self.recording = True
        try:
            self.listener.start()
        except Exception as e:
            self.logger.error(f"Erro ao iniciar a gravação: {e}")
            self.update_signal.emit("Erro na gravação.", 0)

    def stop(self):
        self.recording = False
        try:
            self.listener.stop()
        except Exception as e:
            self.logger.error(f"Erro ao parar a gravação: {e}")
        self.logger.info("Gravação parada. Eventos capturados: %d", len(self.event_manager.get_events()))
        self.update_signal.emit("Gravação parada.", len(self.event_manager.get_events()))

    def play(self):
        self.event_count = 0
        total_events = len(self.event_manager.get_events())
        self.update_signal.emit("Iniciando reprodução...", total_events)
        for event_type, data in self.event_manager.get_events():
            if event_type == EventType.MOUSE_CLICK:
                x, y, button, pressed = data
                self.update_signal.emit(
                    f"Reproduzindo clique do mouse: {x}, {y}, {button}, {'pressionado' if pressed else 'solto'}",
                    total_events)
                if pressed:
                    pyautogui.mouseDown(x, y, button=button.name)
                else:
                    pyautogui.mouseUp(x, y, button=button.name)
                self.event_count += 1
                self.update_signal.emit("Reproduzindo Macro...", self.event_count)



class PontMacroApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.event_manager = EventManager()
        self.recorder = MacroRecorder(self.event_manager)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("PontMacro")
        self.setWindowIcon(QIcon('icon.png'))
        self.setGeometry(100, 100, 800, 600)

        # Aplicando o tema escuro do qdarkstyle
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        # Utilizando GridLayout para melhor organização
        layout = QGridLayout()

        # Estilo para o rótulo de status
        label_style = """
        QLabel {
            font-size: 18px;
            color: white;
        }
        """
        self.status_label = QLabel("Status: Ocioso", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(label_style)

        # Estilo para os botões
        button_style = """
        QPushButton {
            background-color: #3498db;
            color: white;
            font-size: 18px;
            padding: 10px 20px;
            border-radius: 10px;
            border: 2px solid #1A5276;
        }

        QPushButton:hover {
            background-color: #5DADE2;
        }

        QPushButton:pressed {
            background-color: #2E86C1;
        }
        """

        # Criando botões e aplicando estilos
        self.start_button = QPushButton("Iniciar Gravação", self)
        self.stop_button = QPushButton("Parar Gravação", self)
        self.play_button = QPushButton("Reproduzir Macro", self)
        self.save_button = QPushButton("Salvar Macro", self)
        self.load_button = QPushButton("Carregar Macro", self)

        # Adicionando Tooltips
        self.start_button.setToolTip("Iniciar a gravação de uma nova macro")
        self.stop_button.setToolTip("Parar a gravação atual")
        self.play_button.setToolTip("Reproduzir a macro gravada")
        self.save_button.setToolTip("Salvar a macro atual em um arquivo")
        self.load_button.setToolTip("Carregar uma macro de um arquivo")

        # Aplicando estilo aos botões
        self.start_button.setStyleSheet(button_style)
        self.stop_button.setStyleSheet(button_style)
        self.play_button.setStyleSheet(button_style)
        self.save_button.setStyleSheet(button_style)
        self.load_button.setStyleSheet(button_style)

        # Estilo para a barra de progresso
        progress_bar_style = """
        QProgressBar {
            border-radius: 5px;
            background-color: #34495E;
            color: #FFFFFF;
        }

        QProgressBar::chunk {
            background-color: #3498DB;
            border-radius: 5px;
        }
        """
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setStyleSheet(progress_bar_style)

        # Organizando os widgets no layout
        layout.addWidget(self.status_label, 0, 0, 1, 2)  # Ocupando 2 colunas
        layout.addWidget(self.start_button, 1, 0)
        layout.addWidget(self.stop_button, 1, 1)
        layout.addWidget(self.play_button, 2, 0)
        layout.addWidget(self.save_button, 2, 1)
        layout.addWidget(self.load_button, 3, 0)
        layout.addWidget(self.progress_bar, 3, 1)

        # Configurando o container principal
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Conectando sinais
        self.start_button.clicked.connect(self.start_recording)
        self.stop_button.clicked.connect(self.stop_recording)
        self.play_button.clicked.connect(self.play_macro)
        self.save_button.clicked.connect(self.save_macro)
        self.load_button.clicked.connect(self.load_macro)
        self.recorder.update_signal.connect(self.update_status)

        # Configurações iniciais dos botões e da barra de progresso
        self.stop_button.setEnabled(False)
        self.progress_bar.setValue(0)

    def update_status(self, message, progress):
        self.status_label.setText(f"Status: {message}")
        self.progress_bar.setValue(progress)

    def start_recording(self):
        if not self.recorder.isRunning():
            self.event_manager.clear_events()
            self.recorder.start()
            self.update_status("Gravando", len(self.event_manager.get_events()))
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)

    def stop_recording(self):
        self.recorder.stop()
        self.update_status("Ocioso", len(self.event_manager.get_events()))
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def play_macro(self):
        if not self.recorder.isRunning() and self.event_manager.get_events():
            self.recorder.update_signal.connect(self.update_status)
            self.recorder.play()
            self.update_status("Ocioso", len(self.event_manager.get_events()))
        else:
            self.update_status("Nenhum Macro Gravado" if not self.event_manager.get_events() else "Gravador Ocupado",
                               len(self.event_manager.get_events()))

    def save_macro(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Salvar Macro", "", "Macro Files (*.macro)",
                                                  options=options)
        if fileName:
            with open(fileName, 'wb') as file:
                pickle.dump(self.event_manager.get_events(), file)

    def load_macro(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Carregar Macro", "", "Macro Files (*.macro)",
                                                  options=options)
        if fileName:
            with open(fileName, 'rb') as file:
                loaded_events = pickle.load(file)
                self.event_manager.clear_events()
                for event in loaded_events:
                    self.event_manager.add_event(*event)

    def change_theme(self, theme_name):
        if theme_name == "dark":
            self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        elif theme_name == "light":
            self.setStyleSheet("")


if __name__ == "__main__":
    logging.basicConfig(filename="macro_recorder.log", level=logging.INFO,
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    app = QApplication(sys.argv)
    ex = PontMacroApp()
    ex.show()
    sys.exit(app.exec_())

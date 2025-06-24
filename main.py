import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, 
                             QFileDialog, QMessageBox, QScrollArea, QGroupBox, QSlider)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor, QPalette

class TapeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cells = []
        self.head_pos = 0
        self.visible_cells = 31 
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        
        self.init_tape()
        
    def init_tape(self):
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().setParent(None)

        self.cells = []
        for i in range(self.visible_cells):
            cell = QLabel("_")
            cell.setAlignment(Qt.AlignCenter)
            cell.setFixedSize(40, 40)
            cell.setStyleSheet("""
                QLabel {
                    border: 1px solid #444;
                    background-color: #2d2d2d;
                    color: #fff;
                    font-weight: bold;
                    font-size: 16px;
                }
            """)
            self.cells.append(cell)
            self.layout.addWidget(cell)
        
        self.head_indicator = QLabel("↓")
        self.head_indicator.setAlignment(Qt.AlignCenter)
        self.head_indicator.setFixedSize(40, 20)
        self.head_indicator.setStyleSheet("color: #ff5555; font-size: 16px;")
        
        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        tape_row = QWidget()
        tape_row_layout = QHBoxLayout()
        tape_row_layout.setContentsMargins(0, 0, 0, 0)
        tape_row_layout.setSpacing(0)
        for cell in self.cells:
            tape_row_layout.addWidget(cell)
        tape_row.setLayout(tape_row_layout)
        
        head_row = QWidget()
        head_row_layout = QHBoxLayout()
        head_row_layout.setContentsMargins(0, 0, 0, 0)
        head_row_layout.setSpacing(0)
        
        for i in range(self.visible_cells):
            if i == self.visible_cells // 2:
                head_row_layout.addWidget(self.head_indicator)
            else:
                spacer = QLabel("")
                spacer.setFixedSize(40, 20)
                head_row_layout.addWidget(spacer)
        
        head_row.setLayout(head_row_layout)
        
        container_layout.addWidget(tape_row)
        container_layout.addWidget(head_row)
        container.setLayout(container_layout)
        
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().setParent(None)
        self.layout.addWidget(container)
    
    def update_tape(self, tape_data, head_pos):
        center_pos = self.visible_cells // 2
        start_pos = head_pos - center_pos
        end_pos = head_pos + center_pos
        
        for i in range(self.visible_cells):
            pos = start_pos + i
            if pos in tape_data:
                self.cells[i].setText(tape_data[pos])
            else:
                self.cells[i].setText("_")
        
        for i, cell in enumerate(self.cells):
            if i == center_pos:
                cell.setStyleSheet("""
                    QLabel {
                        border: 2px solid #ff5555;
                        background-color: #3d3d3d;
                        color: #fff;
                        font-weight: bold;
                        font-size: 16px;
                    }
                """)
            else:
                cell.setStyleSheet("""
                    QLabel {
                        border: 1px solid #444;
                        background-color: #2d2d2d;
                        color: #fff;
                        font-weight: bold;
                        font-size: 16px;
                    }
                """)


class TuringMachine:
    def __init__(self):
        self.tape = {}
        self.head_pos = 0
        self.rules = {}
        self.state = "q0"  
        self.halted = False

    def reset(self):
        self.tape = {}
        self.head_pos = 0
        self.state = "q0"  
        self.halted = False
        
    def load_rules(self, rules_text):
        self.rules = {}
        for line in rules_text.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                parts = line.split()
                if len(parts) == 5: 
                    current_state = parts[0]
                    read_symbol = parts[1]
                    new_state = parts[2]
                    write_symbol = parts[3]
                    move_direction = parts[4].upper()
                    
                    self.rules[(current_state, read_symbol)] = (new_state, write_symbol, move_direction)
    
    def step(self):
        if self.halted:
            return False
            
        current_symbol = self.tape.get(self.head_pos, "_")
        rule_key = (self.state, current_symbol)
        
        if rule_key in self.rules:
            new_state, write_symbol, move_direction = self.rules[rule_key]
            
            # Update state
            self.state = new_state
            
            # Write symbol
            if write_symbol != "_":
                self.tape[self.head_pos] = write_symbol
            else:
                if self.head_pos in self.tape:
                    del self.tape[self.head_pos]
            
            if move_direction == "R":
                self.head_pos += 1
            elif move_direction == "L":
                self.head_pos -= 1
            elif move_direction == "F": 
                self.halted = True
                
            return True
        else:
            self.halted = True
            return False
    
    def run_until_halt(self):
        while not self.halted:
            self.step()
    
    def get_tape_content(self):
        if not self.tape:
            return ""
        
        min_pos = min(self.tape.keys())
        max_pos = max(self.tape.keys())
        
        result = []
        for pos in range(min_pos, max_pos + 1):
            result.append(self.tape.get(pos, "_"))
        
        return "".join(result)
    
    def load_content(self, input_str):
        self.tape = {}
        for i, char in enumerate(input_str):
            if char != '_': 
                self.tape[i] = char
        self.head_pos = 0


class TuringMachineGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tm = TuringMachine()
        
        # Initialize animation control first
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.step_machine)
        self.animation_speed = 500  # Default speed in ms
        self.is_running = False
        
        self.init_ui()
        self.setWindowTitle("Simulador de Máquina de Turing")
        self.resize(1000, 600)
        
    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #252525;
            }
            QWidget {
                background-color: #252525;
                color: #fff;
            }
            QGroupBox {
                border: 1px solid #444;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QTextEdit, QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #444;
                color: #fff;
                padding: 5px;
            }
            QPushButton {
                background-color: #3d3d3d;
                border: 1px solid #444;
                color: #fff;
                padding: 5px 10px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            QPushButton:pressed {
                background-color: #2d2d2d;
            }
            QSlider::groove:horizontal {
                background: #3d3d3d;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #ff5555;
                border: 1px solid #444;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::sub-page:horizontal {
                background: #ff5555;
                border-radius: 4px;
            }
        """)
        
        self.tape_widget = TapeWidget()
        main_layout.addWidget(self.tape_widget)
        
        state_layout = QHBoxLayout()
        self.state_label = QLabel("Estado: q0")
        self.state_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.status_label = QLabel("Status: Pronto")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        state_layout.addWidget(self.state_label)
        state_layout.addStretch()
        state_layout.addWidget(self.status_label)
        main_layout.addLayout(state_layout)
        
        # Add speed control slider
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Velocidade:"))
        
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(50, 1000)  # 50ms to 1000ms
        self.speed_slider.setValue(500)  # Default to 500ms
        self.speed_slider.setTickPosition(QSlider.TicksBelow)
        self.speed_slider.setTickInterval(100)
        self.speed_slider.valueChanged.connect(self.update_speed)
        speed_layout.addWidget(self.speed_slider)
        
        self.speed_label = QLabel("500 ms")
        self.speed_label.setStyleSheet("min-width: 70px;")
        speed_layout.addWidget(self.speed_label)
        
        main_layout.addLayout(speed_layout)
        
        control_layout = QHBoxLayout()
        self.run_button = QPushButton("Executar")
        self.run_button.clicked.connect(self.run_machine)
        self.step_button = QPushButton("Passo")
        self.step_button.clicked.connect(self.step_machine)
        self.reset_button = QPushButton("Reiniciar")
        self.reset_button.clicked.connect(self.reset_machine)
        self.pause_button = QPushButton("Pausar")
        self.pause_button.clicked.connect(self.pause_machine)
        self.pause_button.setVisible(False)  # Hidden initially
        
        control_layout.addWidget(self.run_button)
        control_layout.addWidget(self.step_button)
        control_layout.addWidget(self.reset_button)
        control_layout.addWidget(self.pause_button)
        main_layout.addLayout(control_layout)
        
        config_group = QGroupBox("Configuração")
        config_layout = QVBoxLayout()
        
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Digite o conteúdo inicial da fita")
        input_layout.addWidget(QLabel("Conteúdo Inicial:"))
        input_layout.addWidget(self.input_field)
        config_layout.addLayout(input_layout)
        
        rules_layout = QVBoxLayout()
        rules_layout.addWidget(QLabel("Regras: EstadoAtual SímboloLido NovoEstado SímboloEscrito Direção"))
        self.rules_edit = QTextEdit()
        self.rules_edit.setPlaceholderText(
            "Digite as regras aqui, uma por linha\n"
            "Exemplo: q0 A q1 B R\n"
            "Use '_' para vazio, 'F' para parar"
        )
        rules_layout.addWidget(self.rules_edit)
        config_layout.addLayout(rules_layout)
        
        file_layout = QHBoxLayout()
        self.load_rules_button = QPushButton("Carregar Regras")
        self.load_rules_button.clicked.connect(self.load_rules_file)
        self.save_rules_button = QPushButton("Salvar Regras")
        self.save_rules_button.clicked.connect(self.save_rules_file)
        file_layout.addWidget(self.load_rules_button)
        file_layout.addWidget(self.save_rules_button)
        config_layout.addLayout(file_layout)
        
        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)
        
        self.update_display()
    
    def update_display(self):
        self.tape_widget.update_tape(self.tm.tape, self.tm.head_pos)
        self.state_label.setText(f"Estado: {self.tm.state}")
        
        if self.tm.halted:
            status = "Parado"
        elif self.is_running:
            status = "Executando"
        else:
            status = "Pronto"
            
        self.status_label.setText(f"Status: {status}")
    
    def run_machine(self):
        if not self.load_rules():
            return
        
        if not self.tm.tape and self.input_field.text():
            self.tm.load_content(self.input_field.text())
        
        # If already halted, reset before running
        if self.tm.halted:
            self.tm.reset()
            if self.input_field.text():
                self.tm.load_content(self.input_field.text())
        
        self.is_running = True
        self.tm.halted = False
        self.update_display()
        
        # Set up UI for running state
        self.run_button.setEnabled(False)
        self.step_button.setEnabled(False)
        self.pause_button.setVisible(True)
        
        # Start the animation timer
        self.animation_timer.start(self.animation_speed)
    
    def step_machine(self):
        if self.tm.halted:
            self.pause_machine()
            return
            
        if not self.load_rules(): 
            self.pause_machine()
            return
            
        if not self.tm.tape and self.input_field.text():
            self.tm.load_content(self.input_field.text())
        
        # Apply visual feedback for the current cell
        self.highlight_current_cell()
        
        # Perform the step
        self.tm.step()
        self.update_display()
        
        # If halted after step, show result
        if self.tm.halted:
            self.pause_machine()
            QMessageBox.information(self, "Resultado", f"Conteúdo final da fita: {self.tm.get_tape_content()}")
    
    def pause_machine(self):
        self.is_running = False
        self.animation_timer.stop()
        
        # Reset UI controls
        self.run_button.setEnabled(True)
        self.step_button.setEnabled(True)
        self.pause_button.setVisible(False)
        
        self.update_display()
    
    def reset_machine(self):
        # Stop any running animation
        self.animation_timer.stop()
        self.is_running = False
        
        # Reset machine state
        self.tm.reset()
        if self.input_field.text():
            self.tm.load_content(self.input_field.text())
        
        # Reset UI controls
        self.run_button.setEnabled(True)
        self.step_button.setEnabled(True)
        self.pause_button.setVisible(False)
        
        self.update_display()
    
    def update_speed(self):
        self.animation_speed = self.speed_slider.value()
        self.speed_label.setText(f"{self.animation_speed} ms")
        
        # Update timer interval if running
        if self.animation_timer.isActive():
            self.animation_timer.setInterval(self.animation_speed)
    
    def highlight_current_cell(self):
        # Apply animation effect to the current cell
        center_pos = self.tape_widget.visible_cells // 2
        current_cell = self.tape_widget.cells[center_pos]
        
        # Create highlight animation
        animation = QPropertyAnimation(current_cell, b"styleSheet")
        animation.setDuration(300)
        animation.setEasingCurve(QEasingCurve.OutQuad)
        
        # Animation sequence
        animation.setKeyValueAt(0, """
            QLabel {
                border: 2px solid #ff5555;
                background-color: #4d3d3d;
                color: #fff;
                font-weight: bold;
                font-size: 16px;
            }
        """)
        animation.setKeyValueAt(0.5, """
            QLabel {
                border: 2px solid #ff5555;
                background-color: #ff5555;
                color: #000;
                font-weight: bold;
                font-size: 16px;
            }
        """)
        animation.setKeyValueAt(1, """
            QLabel {
                border: 2px solid #ff5555;
                background-color: #3d3d3d;
                color: #fff;
                font-weight: bold;
                font-size: 16px;
            }
        """)
        
        animation.start(QPropertyAnimation.DeleteWhenStopped)
    
    def load_rules(self): 
        rules_text = self.rules_edit.toPlainText()
        if rules_text:
            try:
                self.tm.load_rules(rules_text)
                return True
            except Exception as e:
                QMessageBox.warning(self, "Aviso", f"Formato de regras inválido: {str(e)}")
                return False
        else:
            QMessageBox.warning(self, "Aviso", "Nenhuma regra carregada.")
            return False
    
    def load_rules_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Abrir Arquivo de Regras", "", "Arquivos de Máquina de Turing (*.tm);;Todos os Arquivos (*)")
        if file_name:
            try:
                with open(file_name, 'r') as f:
                    content = f.read()
                    self.rules_edit.setPlainText(content)
                    self.tm.load_rules(content)
                    QMessageBox.information(self, "Sucesso", "Regras carregadas com sucesso")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao carregar: {str(e)}")
    
    def save_rules_file(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Salvar Arquivo de Regras", "", "Arquivos de Máquina de Turing (*.tm);;Todos os Arquivos (*)")
        if file_name:
            try:
                with open(file_name, 'w') as f:
                    f.write(self.rules_edit.toPlainText())
                    QMessageBox.information(self, "Sucesso", "Regras salvas com sucesso")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao salvar: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(37, 37, 37))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(45, 45, 45))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    
    window = TuringMachineGUI()
    window.show()
    sys.exit(app.exec_())
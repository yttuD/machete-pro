import sys
import os
import json
import queue
import threading
import pickle
import time
import requests
import collections
import numpy as np
import torch
import faiss
import sounddevice as sd
import soundcard as sc
import subprocess
import keyboard
from faster_whisper import WhisperModel
from sentence_transformers import SentenceTransformer
import warnings

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QLabel, QTextEdit, QGraphicsDropShadowEffect, QHBoxLayout,
                             QPushButton, QComboBox, QRadioButton, QButtonGroup, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QPoint
from PyQt6.QtGui import QColor, QFont, QIcon, QTextCharFormat

warnings.filterwarnings("ignore")

CONFIG_FILE = "config.json"
LLM_ENDPOINT = "http://localhost:1234/v1/chat/completions"
LLM_MODEL = "qwen2.5-coder-7b-instruct"

class AppSignals(QObject):
    update_status = pyqtSignal(str, str)
    append_user = pyqtSignal(str)
    append_llm = pyqtSignal(str)
    llm_interrupted = pyqtSignal()
    llm_done = pyqtSignal()

class AssistantCore:
    def __init__(self, signals: AppSignals):
        self.signals = signals
        self.text_queue = queue.Queue()
        self.interruption_flag = threading.Event()
        
        self.audio_mode = "VAD"
        self.ptt_hotkey = "alt"
        self.device_id = None
        self.is_running = True
        
        self.signals.update_status.emit("Cargando Modelos...", "#f39c12")
        threading.Thread(target=self._load_models, daemon=True).start()

    def set_config(self, device_id, mode, hotkey):
        self.device_id = device_id
        self.audio_mode = mode
        self.ptt_hotkey = hotkey

    def _load_models(self):
        try:
            self.signals.update_status.emit("Cargando LLM en GPU (LM Studio)...", "#f39c12")
            subprocess.run(["lms", "server", "start"], capture_output=True, text=True)
            subprocess.run(["lms", "load", "qwen2.5-coder-7b-instruct"], capture_output=True, text=True, encoding="utf-8", errors="ignore")
            self.signals.update_status.emit("Cargando Whisper y VAD...", "#f39c12")
            
            self.index = faiss.read_index("index_data/faiss_index.bin")
            with open("index_data/documents.pkl", "rb") as f:
                self.documents = pickle.load(f)
            
            titles = [doc["title"] for doc in self.documents]
            self.dynamic_prompt = "Clase sobre bases de datos: "
            for title in titles:
                if len(self.dynamic_prompt) + len(title) > 250:
                    break
                self.dynamic_prompt += title + ", "
            self.dynamic_prompt = self.dynamic_prompt.strip(", ")
            
            self.hotwords = "triple A+C, ACID, FOR UPDATE, BCNF, DKNF, 1NF, 2NF, 3NF, 4NF, 5NF, JOIN, SELECT, ROLLBACK, COMMIT, START TRANSACTION, LM Studio, NoSQL, SQL, MongoDB, MONGOSH, JSON, XML"
            
            self.emb_model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
            self.vad_model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=False, trust_repo=True)
            self.whisper_model = WhisperModel("medium", device="cuda", compute_type="float16")
            
            self.signals.update_status.emit("Modelos Listos. Iniciando Pipeline...", "#27ae60")
            
            threading.Thread(target=self._llm_worker, daemon=True).start()
            threading.Thread(target=self._audio_worker, daemon=True).start()
            
        except Exception as e:
            self.signals.update_status.emit(f"Error de Carga: {e}", "#e74c3c")

    def _get_context(self, query):
        q_emb = self.emb_model.encode([query]).astype("float32")
        D, I = self.index.search(q_emb, k=2)
        context = ""
        for i in range(len(I[0])):
            context += self.documents[I[0][i]]['content'] + "\n\n"
        return context

    def _llm_worker(self):
        while self.is_running:
            try:
                text = self.text_queue.get(timeout=1.0)
            except queue.Empty:
                continue
                
            if text is None: break
            
            context = self._get_context(text)
            prompt = f"Contexto recuperado:\n{context}\nUsuario dijo: {text}"
            
            payload = {
                "model": LLM_MODEL,
                "messages": [
                    {"role": "system", "content": "Sos un asistente de reuniones. Responde de forma ultra concisa basándote SÓLO en el contexto recuperado."},
                    {"role": "user", "content": prompt}
                ],
                "stream": True, "temperature": 0.1
            }
            
            self.interruption_flag.clear()
            self.signals.append_llm.emit("") 
            
            try:
                with requests.post(LLM_ENDPOINT, json=payload, headers={"Content-Type": "application/json"}, stream=True) as response:
                    if response.status_code == 200:
                        for line in response.iter_lines():
                            if self.interruption_flag.is_set():
                                self.signals.llm_interrupted.emit()
                                break
                            if line:
                                dec = line.decode('utf-8')
                                if dec.startswith("data: "):
                                    data_str = dec[6:]
                                    if data_str == "[DONE]": break
                                    try:
                                        data = json.loads(data_str)
                                        if "choices" in data and len(data["choices"]) > 0:
                                            content = data["choices"][0].get("delta", {}).get("content", "")
                                            if content:
                                                self.signals.append_llm.emit(content)
                                    except: pass
                if not self.interruption_flag.is_set():
                    self.signals.llm_done.emit()
            except:
                self.signals.append_llm.emit("\n[Error de conexión con LM Studio]")
                self.signals.llm_done.emit()
                
            self.text_queue.task_done()

    def _audio_worker(self):
        SAMPLE_RATE = 16000
        CHUNK_SIZE = 512

        audio_buffer = []
        preroll_buffer = collections.deque(maxlen=16) # ~0.5 seg de pre-roll
        is_speaking = False
        silence_counter = 0
        SILENCE_CHUNKS_THRESHOLD = 24
        
        last_device = None
        mic_stream = None
        
        while self.is_running:
            if self.device_id is None:
                time.sleep(1)
                continue
                
            if mic_stream is None or last_device != self.device_id:
                if mic_stream is not None:
                    try:
                        mic_stream.__exit__(None, None, None)
                    except: pass
                last_device = self.device_id
                try:
                    mics = sc.all_microphones(include_loopback=True)
                    if self.device_id >= len(mics):
                        raise ValueError("ID de dispositivo inválido")
                        
                    mic = mics[self.device_id]
                    mic_stream = mic.recorder(samplerate=SAMPLE_RATE, channels=1).__enter__()
                    self.signals.update_status.emit("Escuchando...", "#3498db")
                except Exception as e:
                    print(f"Error al abrir el micrófono {self.device_id}: {e}")
                    self.signals.update_status.emit(f"Error Micrófono", "#e74c3c")
                    mic_stream = None
                    time.sleep(2)
                    continue
            
            try:
                data = mic_stream.record(numframes=CHUNK_SIZE)
                chunk = data.flatten()
            except Exception as e:
                time.sleep(0.1)
                continue
                
            if self.audio_mode == "PTT":
                try:
                    is_pressed = keyboard.is_pressed(self.ptt_hotkey)
                except:
                    is_pressed = False
                    
                if is_pressed:
                    if not is_speaking:
                        is_speaking = True
                        self.interruption_flag.set()
                        audio_buffer = []
                        self.signals.update_status.emit("Grabando (PTT)...", "#f1c40f")
                    audio_buffer.extend(chunk.tolist())
                else:
                    if is_speaking:
                        is_speaking = False
                        self.signals.update_status.emit("Procesando (Whisper)...", "#9b59b6")
                        speech_audio = np.array(audio_buffer, dtype=np.float32)
                        
                        segments, _ = self.whisper_model.transcribe(speech_audio, beam_size=5, language="es", initial_prompt=self.dynamic_prompt)
                        text = "".join([s.text for s in segments]).strip()
                        
                        if len(text) > 3:
                            self.signals.append_user.emit(text)
                            self.text_queue.put(text)
                        
                        self.signals.update_status.emit("Escuchando...", "#3498db")
            else: # VAD Auto
                audio_tensor = torch.from_numpy(chunk.astype(np.float32))
                speech_prob = self.vad_model(audio_tensor, SAMPLE_RATE).item()
                
                if speech_prob > 0.5:
                    if not is_speaking:
                        is_speaking = True
                        self.interruption_flag.set()
                        audio_buffer = []
                        for pr_chunk in preroll_buffer:
                            audio_buffer.extend(pr_chunk.tolist())
                        self.signals.update_status.emit("Capturando voz (VAD)...", "#f1c40f")
                    silence_counter = 0
                    audio_buffer.extend(chunk.tolist())
                else:
                    if is_speaking:
                        audio_buffer.extend(chunk.tolist())
                        silence_counter += 1
                        if silence_counter >= SILENCE_CHUNKS_THRESHOLD:
                            is_speaking = False
                            preroll_buffer.clear()
                            self.signals.update_status.emit("Procesando (Whisper)...", "#9b59b6")
                            speech_audio = np.array(audio_buffer, dtype=np.float32)
                            
                            segments, _ = self.whisper_model.transcribe(speech_audio, beam_size=5, language="es", initial_prompt=self.dynamic_prompt, hotwords=self.hotwords)
                            text = "".join([s.text for s in segments]).strip()
                            
                            if len(text) > 3:
                                self.signals.append_user.emit(text)
                                self.text_queue.put(text)
                            
                            self.signals.update_status.emit("Escuchando...", "#3498db")
                    else:
                        preroll_buffer.append(chunk)
        if mic_stream:
            try:
                mic_stream.__exit__(None, None, None)
            except: pass


class OverlayApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(500, 650)
        
        self.central = QWidget(self)
        self.setCentralWidget(self.central)
        self.central.setStyleSheet("""
            QWidget {
                background-color: rgba(25, 25, 30, 240);
                border-radius: 15px;
                color: #ecf0f1;
                font-family: 'Segoe UI', system-ui, sans-serif;
            }
            #closeBtn {
                background-color: transparent;
                border-radius: 12px;
                color: #e74c3c;
            }
            #closeBtn:hover {
                background-color: #e74c3c;
                color: white;
            }
            #configPanel {
                background-color: rgba(255, 255, 255, 10);
                border-radius: 10px;
            }
            QComboBox {
                background-color: rgba(0, 0, 0, 80);
                border-radius: 6px;
                padding: 5px 10px;
                border: 1px solid rgba(255, 255, 255, 20);
            }
            QComboBox:hover {
                border: 1px solid rgba(255, 255, 255, 50);
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QRadioButton {
                spacing: 8px;
                font-size: 13px;
            }
            QRadioButton::indicator {
                width: 14px;
                height: 14px;
                border-radius: 7px;
                background-color: rgba(0, 0, 0, 80);
                border: 1px solid rgba(255,255,255,40);
            }
            QRadioButton::indicator:checked {
                background-color: #3498db;
                border: 2px solid #2980b9;
            }
            QLabel {
                background: transparent;
                border: none;
            }
            QTextEdit {
                background-color: rgba(0, 0, 0, 70);
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                line-height: 1.5;
                border: 1px solid rgba(255, 255, 255, 10);
            }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 40);
                border-radius: 4px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.central.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self.central)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        # Header HBox
        header_layout = QHBoxLayout()
        self.header = QLabel("✨ AI Meeting Assistant")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: #ecf0f1;")
        header_layout.addWidget(self.header)
        header_layout.addStretch()
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.close_btn.clicked.connect(self.close)
        header_layout.addWidget(self.close_btn)
        
        layout.addLayout(header_layout)
        
        # Config Area
        self.config_frame = QFrame()
        self.config_frame.setObjectName("configPanel")
        config_layout = QVBoxLayout(self.config_frame)
        config_layout.setContentsMargins(12, 12, 12, 12)
        config_layout.setSpacing(10)
        
        dev_layout = QHBoxLayout()
        dev_lbl = QLabel("🎙️ Micrófono:")
        dev_lbl.setStyleSheet("font-weight: bold; color: #bdc3c7;")
        dev_layout.addWidget(dev_lbl)
        self.device_combo = QComboBox()
        self.device_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.populate_devices()
        dev_layout.addWidget(self.device_combo, stretch=1)
        config_layout.addLayout(dev_layout)
        
        mode_layout = QHBoxLayout()
        self.btn_vad = QRadioButton("Auto (VAD)")
        self.btn_ptt = QRadioButton("Presionar para Hablar")
        self.btn_vad.setChecked(True)
        mode_layout.addWidget(self.btn_vad)
        mode_layout.addWidget(self.btn_ptt)
        
        self.hotkey_combo = QComboBox()
        self.hotkey_combo.addItems(["alt", "ctrl", "shift", "space", "f9", "f10"])
        mode_layout.addWidget(QLabel("⌨️ Tecla:"))
        mode_layout.addWidget(self.hotkey_combo)
        
        config_layout.addLayout(mode_layout)
        layout.addWidget(self.config_frame)
        
        # Status
        self.status_lbl = QLabel("Iniciando...")
        self.status_lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #bdc3c7; padding-top: 2px;")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_lbl)
        
        # Chat
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)
        
        self.old_pos = None
        
        self.signals = AppSignals()
        self.signals.update_status.connect(self.update_status)
        self.signals.append_user.connect(self.append_user)
        self.signals.append_llm.connect(self.append_llm)
        self.signals.llm_interrupted.connect(self.llm_interrupted)
        self.signals.llm_done.connect(self.llm_done)
        
        self.core = AssistantCore(self.signals)
        self.current_llm_block = False
        
        # Connect config changes
        self.device_combo.currentIndexChanged.connect(self.update_core_config)
        self.btn_vad.toggled.connect(self.update_core_config)
        self.hotkey_combo.currentTextChanged.connect(self.update_core_config)
        
        # Initial config
        self.update_core_config()

    def populate_devices(self):
        selected_idx = 0
        saved = -1
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    saved = json.load(f).get("device_index", -1)
            except: pass
                
        self.device_combo.clear()
        try:
            mics = sc.all_microphones(include_loopback=True)
            for i, mic in enumerate(mics):
                prefix = "🔊 [Loopback] " if mic.isloopback else "🎤 "
                self.device_combo.addItem(f"{prefix}[{i}] {mic.name}", userData=i)
                if saved == i:
                    selected_idx = self.device_combo.count() - 1
        except Exception as e:
            print("Error cargando dispositivos:", e)
            
        self.device_combo.setCurrentIndex(selected_idx)
        self.device_combo.setCurrentIndex(selected_idx)

    def update_core_config(self):
        dev_id = self.device_combo.currentData()
        mode = "VAD" if self.btn_vad.isChecked() else "PTT"
        hotkey = self.hotkey_combo.currentText()
        
        if dev_id is not None:
            with open(CONFIG_FILE, "w") as f:
                json.dump({"device_index": dev_id}, f)
            self.core.set_config(dev_id, mode, hotkey)

    def update_status(self, text, color):
        self.status_lbl.setText(text)
        self.status_lbl.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {color}; border: none; background: transparent;")

    def append_user(self, text):
        html = f'<div style="color: #3498db; margin-top: 10px;"><b>Tú:</b> {text}</div>'
        self.chat_display.append(html)
        self.current_llm_block = False

    def append_llm(self, text):
        if not self.current_llm_block:
            self.chat_display.append('<div style="color: #2ecc71; margin-top: 5px;"><b>Asistente:</b> </div>')
            self.current_llm_block = True
            
        cursor = self.chat_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#ecf0f1"))
        cursor.insertText(text, fmt)
        
        self.chat_display.setTextCursor(cursor)
        self.chat_display.ensureCursorVisible()

    def llm_interrupted(self):
        self.chat_display.insertHtml('&nbsp;<span style="color: #e74c3c;"><i>[Interrumpido]</i></span>')
        self.current_llm_block = False
        
    def llm_done(self):
        self.current_llm_block = False

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def closeEvent(self, event):
        self.status_lbl.setText("Apagando y liberando VRAM...")
        self.core.is_running = False
        subprocess.Popen(["lms", "unload", "--all"])
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = OverlayApp()
    window.show()
    sys.exit(app.exec())

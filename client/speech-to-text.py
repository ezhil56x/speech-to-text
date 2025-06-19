import sys
import threading
import tempfile
import os
import requests
import sounddevice as sd
import scipy.io.wavfile as wav
from pynput import keyboard
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject, pyqtSignal

fs = 16000
kb_controller = keyboard.Controller()

class Communicate(QObject):
    status_update = pyqtSignal(str)

class RecorderTrayApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.tray_icon = QSystemTrayIcon(QIcon("robot.png"))
        self.menu = QMenu()

        self.quit_action = QAction("Quit")
        self.quit_action.triggered.connect(self.quit_app)

        self.menu.addAction(self.quit_action)
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.setToolTip("Status: Idle")
        self.tray_icon.show()

        self.c = Communicate()
        self.c.status_update.connect(self.update_status)

        self.recording_active = False
        self.recording_thread = None

    def update_status(self, status):
        self.tray_icon.setToolTip(f"Status: {status}")

    def record_audio_to_file(self):
        self.c.status_update.emit("Recording...")
        audio = sd.rec(int(60 * fs), samplerate=fs, channels=1, dtype='int16')
        return audio

    def stop_and_save_audio(self, audio_data, frames):
        sd.stop()
        audio_data = audio_data[:frames]
        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        wav.write(temp_wav.name, fs, audio_data)
        return temp_wav.name

    def send_audio_to_docker(self, wav_file_path):
        url = "http://localhost:5005/transcribe"
        try:
            with open(wav_file_path, "rb") as f:
                response = requests.post(url, files={"file": f})
            response.raise_for_status()
            text = response.json().get("text", "")
            return text
        except Exception as e:
            print("[ERROR] Transcription failed:", e)
            return ""

    def type_text(self, text):
        for char in text:
            kb_controller.press(char)
            kb_controller.release(char)

    def handle_recording(self):
        frames = 0
        audio_buffer = self.record_audio_to_file()
        while self.recording_active:
            sd.sleep(100)
            frames += int(0.1 * fs)

        wav_path = self.stop_and_save_audio(audio_buffer, frames)
        self.c.status_update.emit("Transcribing...")
        transcription = self.send_audio_to_docker(wav_path)
        os.remove(wav_path)
        if transcription:
            self.type_text(transcription)
        self.c.status_update.emit("Idle")

    def on_press(self, key):
        if key == keyboard.Key.f9 and not self.recording_active:
            self.recording_active = True
            self.recording_thread = threading.Thread(target=self.handle_recording)
            self.recording_thread.start()

    def on_release(self, key):
        if key == keyboard.Key.f9 and self.recording_active:
            self.recording_active = False

    def start_listener(self):
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()

    def quit_app(self):
        self.recording_active = False
        self.tray_icon.hide()
        self.app.quit()

    def run(self):
        listener_thread = threading.Thread(target=self.start_listener, daemon=True)
        listener_thread.start()
        sys.exit(self.app.exec())

if __name__ == "__main__":
    tray_app = RecorderTrayApp()
    tray_app.run()

import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import subprocess
import speech_recognition as sr
import requests
import json
import threading
import logging
import sys
from pathlib import Path

# --- 1. Logging-Konfiguration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("chatbot.log"), # Loggt in eine Datei
        logging.StreamHandler() # Loggt auch in die Konsole
    ]
)

# --- 2. Verbesserte Chatbot-Klasse mit Fehlerbehandlung ---
class Chatbot:
    def __init__(self):
        self.voice_map = {
            'en': ('Karen', 'en-US'),
            'it': ('Alice', 'it-IT'),
            'sv': ('Alva', 'sv-SE'),
            'fr': ('Amelie', 'fr-FR'),
            'de': ('Anna', 'de-DE'),
            'ar': ('Majed', 'ar-SA')
        }
        self.api_url = "http://localhost:11434/api/generate"
    
    def text_to_speech(self, text, language='en', slow=True):
        if sys.platform != 'darwin':
            logging.warning("Text-to-Speech mit 'say' ist nur auf macOS verfügbar. Überspringe.")
            # Hier könnte man eine plattformübergreifende Alternative wie pyttsx3 einbauen
            return

        rate = 180 if slow else 350
        voice = self.voice_map.get(language, ('Karen', 'en-US'))[0]
        command = ['say', '-v', voice, '-r', str(rate), text]
        
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            logging.info(f"Sprachausgabe erfolgreich für Text: '{text[:30]}...'")
        except FileNotFoundError:
            logging.error("Der Befehl 'say' wurde nicht gefunden. Ist dies ein macOS-System?")
            raise
        except subprocess.CalledProcessError as e:
            logging.error(f"Fehler bei der Sprachausgabe: {e.stderr}")
            raise

    def speech_to_text(self, language='en'):
        recognizer = sr.Recognizer()
        lang_code = self.voice_map.get(language, ('Karen', 'en-US'))[1]
        
        try:
            with sr.Microphone() as source:
                logging.info("Höre zu...")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        except AttributeError:
            logging.error("Kein Mikrofon gefunden (AttributeError in sr.Microphone).")
            raise ConnectionError("Kein Mikrofon gefunden. Stellen Sie sicher, dass eines angeschlossen ist.")
        except Exception as e:
            logging.error(f"Fehler beim Zugriff auf das Mikrofon: {e}")
            raise
        
        try:
            logging.info("Erkenne Sprache...")
            text = recognizer.recognize_google(audio, language=lang_code)
            logging.info(f"Erkannter Text: {text}")
            return text
        except sr.UnknownValueError:
            logging.warning("Sprache konnte nicht verstanden werden.")
            raise sr.UnknownValueError("Ich konnte das nicht verstehen.")
        except sr.RequestError as e:
            logging.error(f"Google Speech Recognition Service Fehler: {e}")
            raise sr.RequestError(f"Verbindungsfehler zum Sprachdienst.")

    def generate_response(self, prompt: str):
        input_data = {
            "model": "llama3.2:1b", # Du kannst hier dein Modell anpassen
            "prompt": prompt,
            "stream": False # Wir nutzen nicht-streaming für eine einfachere Fehlerbehandlung
        }
        
        try:
            response = requests.post(self.api_url, json=input_data, timeout=60)
            response.raise_for_status() # Löst einen Fehler bei 4xx/5xx Antworten aus
            
            json_response = response.json()
            logging.info(f"Antwort von Ollama erhalten.")
            return json_response.get('response', "Keine 'response' im JSON gefunden.").strip()

        except requests.exceptions.RequestException as e:
            logging.error(f"Fehler bei der Anfrage an Ollama: {e}")
            raise ConnectionError("Verbindung zum Ollama-Server fehlgeschlagen.")
        except json.JSONDecodeError:
            logging.error("Ungültige JSON-Antwort von Ollama erhalten.")
            raise ValueError("Ungültige Antwort vom Server erhalten.")

# --- 3. Verbesserte GUI-Klasse ---
class ChatbotUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Moderner Chatbot")
        self.master.geometry("800x600")
        self.chatbot = Chatbot()
        self.is_processing = False
        
        # Style Konfiguration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        self.create_widgets()
        logging.info("Chatbot-UI initialisiert.")

    def configure_styles(self):
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TButton", background="#0078D7", foreground="white", font=("Segoe UI", 10, "bold"), borderwidth=0)
        self.style.map("TButton", background=[('active', '#005a9e')])
        self.style.configure("Status.TLabel", padding=10, font=("Segoe UI", 9))
        self.style.configure("User.TLabel", background="#0078D7", foreground="white")
        self.style.configure("Bot.TLabel", background="#e1e1e1", foreground="black")

    def create_widgets(self):
        # Grid Layout Konfiguration
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)

        # Haupt-Frame
        main_frame = ttk.Frame(self.master, style="TFrame")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # Chat-Verlauf (jetzt mit Tags für Bubbles)
        self.chat_history = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, state="disabled",
                                                      font=("Segoe UI", 11), bg="white", relief="solid", borderwidth=1)
        self.chat_history.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        self.chat_history.tag_configure("user", justify="right", background="#0078D7", foreground="white",
                                        relief="raised", borderwidth=2, lmargin1=60, lmargin2=60, spacing3=10)
        self.chat_history.tag_configure("bot", justify="left", background="#e1e1e1", foreground="black",
                                                relief="raised", borderwidth=2, lmargin1=10, lmargin2=10, spacing3=10)
        self.chat_history.tag_configure("error", foreground="red", font=("Segoe UI", 10, "italic"))

        # Input Frame
        input_frame = ttk.Frame(main_frame, style="TFrame", padding=10)
        input_frame.grid(row=1, column=0, sticky="ew")
        input_frame.columnconfigure(0, weight=1)

        self.input_field = ttk.Entry(input_frame, font=("Segoe UI", 11))
        self.input_field.grid(row=0, column=0, sticky="ew")
        self.input_field.bind("<Return>", self.send_message)

        # Icon laden
        icon_path = Path(__file__).parent / "icons"
        try:
            self.send_icon = tk.PhotoImage(file=icon_path / "send.png").subsample(2, 2)
            self.speak_icon = tk.PhotoImage(file=icon_path / "microphone.png").subsample(2, 2)
        except tk.TclError:
            self.send_icon, self.speak_icon = None, None
            logging.warning("Icons nicht gefunden. Buttons werden ohne Bilder angezeigt.")

        self.send_button = ttk.Button(input_frame, text=" Senden", command=self.send_message, image=self.send_icon, compound="left")
        self.send_button.grid(row=0, column=1, padx=(5, 0))

        self.speak_button = ttk.Button(input_frame, text=" Sprechen", command=self.speak, image=self.speak_icon, compound="left")
        self.speak_button.grid(row=0, column=2, padx=5)
        
        # Options Frame
        options_frame = ttk.Frame(main_frame, style="TFrame", padding=(10, 0, 10, 10))
        options_frame.grid(row=2, column=0, sticky="ew")
        
        ttk.Label(options_frame, text="Sprache:", font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.language_combobox = ttk.Combobox(options_frame, values=list(self.chatbot.voice_map.keys()), state="readonly")
        self.language_combobox.set('de')
        self.language_combobox.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(options_frame, text="Stop", command=self.stop_processing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.RIGHT)
        
        # Status-Label
        self.status_label = ttk.Label(self.master, text="Bereit", style="Status.TLabel", background="#e1e1e1", anchor="w")
        self.status_label.grid(row=1, column=0, sticky="ew")
        self.show_status("Bereit", "black")

    def show_status(self, message, color):
        self.status_label.config(text=message, foreground=color)
        self.master.update_idletasks()

    def update_chat_history(self, message, tag):
        self.chat_history.config(state="normal")
        self.chat_history.insert(tk.END, f"{message}\n\n", tag)
        self.chat_history.config(state="disabled")
        self.chat_history.see(tk.END)

    def set_processing_state(self, is_processing):
        self.is_processing = is_processing
        state = tk.NORMAL if not is_processing else tk.DISABLED
        self.send_button.config(state=state)
        self.speak_button.config(state=state)
        self.stop_button.config(state=tk.NORMAL if is_processing else tk.DISABLED)

    def send_message(self, event=None):
        message = self.input_field.get().strip()
        if message and not self.is_processing:
            self.update_chat_history(message, "user")
            self.input_field.delete(0, tk.END)
            
            self.set_processing_state(True)
            self.show_status("Denke nach...", "blue")
            
            threading.Thread(target=self.process_message, args=(message,)).start()

    def speak(self):
        if not self.is_processing:
            self.set_processing_state(True)
            self.show_status("Höre zu...", "blue")
            threading.Thread(target=self.process_speech).start()
            
    def process_message(self, message):
        try:
            response = self.chatbot.generate_response(message)
            if not self.is_processing: return
            
            self.master.after(0, self.update_chat_history, response, "bot")
            self.chatbot.text_to_speech(response, self.language_combobox.get())
            
        except (ConnectionError, ValueError, sr.RequestError) as e:
            if not self.is_processing: return
            logging.error(f"Ein Fehler ist aufgetreten: {e}")
            self.master.after(0, self.update_chat_history, f"Fehler: {e}", "error")
        finally:
            if not self.is_processing: return
            self.master.after(0, self.reset_ui)

    def process_speech(self):
        try:
            spoken_text = self.chatbot.speech_to_text(self.language_combobox.get())
            if not self.is_processing: return

            self.master.after(0, self.update_chat_history, spoken_text, "user")
            self.master.after(0, self.show_status, "Denke nach...", "blue")
            self.process_message(spoken_text)

        except (sr.UnknownValueError, sr.RequestError, ConnectionError) as e:
            if not self.is_processing: return
            logging.error(f"Spracherkennung fehlgeschlagen: {e}")
            self.master.after(0, self.update_chat_history, f"Fehler: {e}", "error")
            self.master.after(0, self.reset_ui)

    def stop_processing(self):
        """Beendet alle laufenden Prozesse und setzt die UI zurück."""
        logging.info("Verarbeitung durch Nutzer abgebrochen.")
        
        # Setze Verarbeitungs-Flag
        self.is_processing = False
        
        # Stoppe eventuelle Sprachausgabe (macOS spezifisch)
        try:
            subprocess.run(['pkill', '-f', 'say'], check=False)
        except Exception as e:
            logging.warning(f"Fehler beim Beenden der Sprachausgabe: {e}")
        
        # Setze UI-Elemente zurück
        self.reset_ui()
        self.show_status("Abgebrochen", "orange")
        
        # Warte kurz und setze dann den Status auf "Bereit"
        self.master.after(1500, lambda: self.show_status("Bereit", "black"))

    def reset_ui(self):
        self.set_processing_state(False)
        self.show_status("Bereit", "black")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        ui = ChatbotUI(root)
        root.mainloop()
    except Exception as e:
        logging.critical(f"Ein unerwarteter Fehler hat die Anwendung beendet: {e}")
        messagebox.showerror("Kritischer Fehler", f"Die Anwendung muss beendet werden:\n{e}")
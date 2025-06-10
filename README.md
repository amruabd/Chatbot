# Desktop Chatbot mit Sprachsteuerung und lokaler LLM-Anbindung

Dieses Projekt ist eine Desktop-Anwendung für einen Chatbot, die mit Python und Tkinter erstellt wurde. Der Chatbot kann sowohl über Texteingabe als auch über Sprache gesteuert werden und gibt Antworten als Text und über eine synthetische Stimme aus. Die eigentliche Intelligenz des Chatbots wird durch ein lokal laufendes Large Language Model (LLM) über die [Ollama-Plattform] bereitgestellt.

---

## ✨ Funktionen

- **Grafische Benutzeroberfläche (GUI):** Eine einfache und intuitive Oberfläche, gebaut mit `Tkinter`.
- **Lokale LLM-Integration:** Verbindet sich mit einem lokal laufenden Ollama-Server, um Anfragen zu verarbeiten. Dies gewährleistet Datenschutz und Offline-Fähigkeit.
- **Texteingabe:** Klassische Chat-Funktionalität über ein Eingabefeld.
- **Spracherkennung (Speech-to-Text):** Nutzt die `SpeechRecognition`-Bibliothek, um gesprochene Anfragen in Text umzuwandeln.
- **Sprachausgabe (Text-to-Speech):** Gibt die Antworten des Chatbots über die systemeigene `say`-Funktion von macOS aus.
- **Mehrsprachigkeit:** Unterstützt verschiedene Sprachen für die Sprachausgabe (u.a. Englisch, Deutsch, Italienisch, Französisch).
- **Asynchrone Verarbeitung:** Verwendet `threading`, um die GUI reaktionsfähig zu halten, während Anfragen an das LLM gesendet oder Sprache verarbeitet wird.
- **Stop-Funktion:** Ermöglicht das Abbrechen einer laufenden Anfrage.

---

## 🛠️ Technische Details

- **Sprache:** Python 3
- **GUI:** Tkinter
- **LLM-Anbindung:** [Ollama API](https://github.com/ollama/ollama/blob/main/docs/api.md) via `requests`
- **Spracherkennung:** `SpeechRecognition` (mit Google Speech Recognition API)
- **Sprachausgabe:** `say` Kommandozeilen-Tool (nativ auf macOS)

---

## 🚀 Voraussetzungen

Bevor du das Projekt startest, stelle sicher, dass die folgenden Anforderungen erfüllt sind:

1.  **Python 3:** Du benötigst eine installierte Version von Python 3.
2.  **Ollama:** Du musst [Ollama](https://ollama.com/) installiert und gestartet haben. Der Chatbot verbindet sich mit dem Standard-Port `11434`.
3.  **Ein LLM-Modell:** Du musst mindestens ein Modell über Ollama heruntergeladen haben. Der Code ist für `phi3` oder `llama3` vorkonfiguriert.

    ```bash
    # Lade das Phi-3 Modell (empfohlen für eine gute Balance aus Geschwindigkeit und Leistung)
    ollama pull phi3

    # Oder lade Llama 3
    ollama pull llama3
    ```

4.  **Betriebssystem:** Die Sprachausgabe (`text_to_speech`) verwendet den `say`-Befehl, der **standardmäßig nur auf macOS verfügbar ist**. Für Windows oder Linux muss diese Funktion angepasst werden (siehe Abschnitt _Anpassung_).
5.  **Mikrofon:** Ein funktionierendes Mikrofon wird für die Spracherkennung benötigt.
6.  **Internetverbindung:** Die Spracherkennung verwendet die Google Speech Recognition API und erfordert daher eine aktive Internetverbindung.

---

## ⚙️ Installation & Einrichtung

1.  **Klone das Repository:**

    ```bash
    git clone https://github.com/dein-benutzername/dein-projekt.git
    cd dein-projekt
    ```

2.  **Erstelle eine virtuelle Umgebung (empfohlen):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Auf macOS/Linux
    # venv\Scripts\activate   # Auf Windows
    ```

3.  **Installiere die Abhängigkeiten:**
    Erstelle eine Datei namens `requirements.txt` mit dem folgenden Inhalt:
    ```txt
    requests
    SpeechRecognition
    PyAudio
    ```
    Installiere sie dann mit pip:
    ```bash
    pip install -r requirements.txt
    ```

---

## ▶️ Verwendung

1.  **Starte Ollama:** Stelle sicher, dass der Ollama-Dienst im Hintergrund läuft.
2.  **Starte die Anwendung:** Führe das Python-Skript aus.
    ```bash
    python chatbot.py
    ```
3.  **Benutze den Chatbot:**
    - Wähle die gewünschte Sprache für die Sprachausgabe aus dem Dropdown-Menü.
    - Gib deine Frage in das Textfeld ein und drücke `Enter` oder klicke auf "Senden".
    - Klicke auf "Sprechen", um eine Frage über dein Mikrofon zu stellen.
    - Die Antwort des Chatbots erscheint im Chatfenster und wird vorgelesen.

---

## 🔧 Personalisierung & Anpassung

### LLM-Modell ändern

Du kannst jedes von Ollama unterstützte Modell verwenden. Ändere einfach den Modellnamen in der `generate_response`-Funktion in `chatbot.py`:

```python
def generate_response(self, prompt):
    input_data = {
        "model": "phi3:latest",  # Ändere dies z.B. zu "llama3:latest" oder "mistral:latest"
        "prompt": prompt,
    }
    # ...
```

### Sprachausgabe für Windows/Linux anpassen

Die `text_to_speech`-Funktion muss für andere Betriebssysteme als macOS angepasst werden. Eine beliebte plattformübergreifende Bibliothek dafür ist `pyttsx3`.

1.  **Installiere `pyttsx3`:**
    ```bash
    pip install pyttsx3
    ```
2.  **Passe die Funktion an:**
    Ersetze die `text_to_speech`-Funktion in `chatbot.py` durch diese Version:

    ```python
    import pyttsx3

    class Chatbot:
        def __init__(self):
            # ... dein bisheriger init-Code ...
            self.tts_engine = pyttsx3.init()

        def text_to_speech(self, text, language='en', slow=True):
            rate = 180 if slow else 350
            self.tts_engine.setProperty('rate', rate)

            # Hinweis: Die Sprachauswahl mit pyttsx3 ist komplexer und systemabhängig.
            # Dies ist eine einfache Implementierung.
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()

    ```

---

## 📜 Lizenz

Dieses Projekt steht unter der [MIT-Lizenz](LICENSE).

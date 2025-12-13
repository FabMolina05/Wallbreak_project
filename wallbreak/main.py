import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play
import pyttsx3
import threading
from google import genai
import tkinter as tk

# CONFIGURACIÓN

client = genai.Client(api_key="AIzaSyBEQRCjHyVHg6smwCabwTHz1xJvu4uSz78")

flag = False
lock = threading.Lock()

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[2].id)

r = sr.Recognizer()

# FUNCIONES UI

def actualizar_texto(original, traduccion):
    output_text.configure(state="normal")
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, f"🗣 Tú dijiste:\n{original}\n\n")
    output_text.insert(tk.END, f"🌍 Traducción:\n{traduccion}")
    output_text.configure(state="disabled")

# LÓGICA

def output_voice(audio):
    try:
        global flag
        text = r.recognize_google(audio, language="es-ES")
        print("Has dicho:", text)

        with lock:
            if text.lower() == "salir":
                flag = False
                root.after(0, lambda: status_label.config(text="Estado: detenido"))
                return

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Tradúceme esto al inglés: {text}, sin texto adicional"
        )

        engine.say(response.text)
        engine.runAndWait()
        engine.stop()

        print("Traducción:", response.text)

        # actualizar UI de forma segura
        root.after(0, actualizar_texto, text, response.text)

    except sr.UnknownValueError:
        print("No se pudo entender el audio")
    except sr.RequestError as e:
        print("Error:", e)

# BUCLE DE ESCUCHA

def escuchar():
    global flag
    while flag:
        with sr.Microphone(device_index=0) as source:
            audio = r.listen(source)
            threading.Thread(target=output_voice, args=(audio,), daemon=True).start()

# BOTONES

def iniciar():
    global flag
    if not flag:
        flag = True
        status_label.config(text="Estado: escuchando")
        threading.Thread(target=escuchar, daemon=True).start()

def detener():
    global flag
    flag = False
    status_label.config(text="Estado: detenido")

# INTERFAZ TKINTER

root = tk.Tk()
root.title("Wallbreak - Traductor por Voz")
root.geometry("420x350")
root.resizable(False, False)

tk.Label(root, text="Wallbreak", font=("Arial", 16)).pack(pady=5)

status_label = tk.Label(root, text="Estado: detenido")
status_label.pack()

output_text = tk.Text(root, height=10, width=45, state="disabled")
output_text.pack(pady=10)

tk.Button(root, text="Iniciar", width=15, command=iniciar).pack(pady=3)
tk.Button(root, text="Detener", width=15, command=detener).pack(pady=3)

root.mainloop()

import queue
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play
import pyttsx3
import threading
from google import genai
import time

# Dispositivos de audio disponibles
#m = None
#for i, microphone_name in enumerate(sr.Microphone.list_microphone_names()):
#   print(f"Microphone with name \"{microphone_name}\" found for `Microphone(device_index={i})`")


# Variables globales
client = genai.Client(api_key="AIzaSyBEQRCjHyVHg6smwCabwTHz1xJvu4uSz78")

flag = True

lock = threading.Lock()

r = sr.Recognizer()

text_queue = queue.Queue()

stop_event = threading.Event()

####################

##Worker TTS
def tts_worker():
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[2].id)
    print("TTS Hilo iniciado")
    engine.startLoop(False)
    while not stop_event.is_set():
        try:
            text = text_queue.get(timeout=1)
            print(f"Procesando texto: {text}")
            engine.say(text)
            engine.iterate()
            text_queue.task_done()
            print("TTS completado")
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Error en TTS: {e}")
            
    print("TTS Hilo terminado")
    engine.endLoop()
    engine.stop()

def output_voice(tiempo,text,r=r,):
    print("Hilo iniciado")
    global flag
    try:
        with lock:
            print("Has dicho: {}".format(text))
            if text.lower() == "salir":
                flag = False
                stop_event.set()
                print("Saliendo...")
                return
            response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=f"Tradúceme esto al inglés: {text}, hazlo informal y sin texto extra.",
            )
            print("llego hasta aqui")
            text_queue.put(response.text)
            tiempo_final = time.time()
            print(f"Tiempo de respuesta: {tiempo_final - tiempo} segundos")
    except sr.UnknownValueError:
        print("No se pudo entender el audio")
            


##Run Process
hilo_tts = threading.Thread(target=tts_worker)
hilo_tts.start()
while flag:
    tiempo_inicial = time.time()
    try:
        with sr.Microphone(device_index=0) as source:
            if not flag:
                break
            print("Di algo...")
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source,phrase_time_limit=2) 
            text = r.recognize_google(audio, language="es-ES")

            
            hilo = threading.Thread(target=output_voice, args=(tiempo_inicial,text,))
            hilo.start()
                
                
    except sr.UnknownValueError:
        print("No se pudo entender el audio en el while")
    except sr.RequestError as e:
        print(f"Error al solicitar resultados; {e}")     

print("Fuera del while")  

    
        

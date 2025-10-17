import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play
import pyttsx3
import threading
from google import genai
# Dispositivos de audio disponibles
#m = None
#for i, microphone_name in enumerate(sr.Microphone.list_microphone_names()):
#   print(f"Microphone with name \"{microphone_name}\" found for `Microphone(device_index={i})`")


client = genai.Client(api_key="AIzaSyBEQRCjHyVHg6smwCabwTHz1xJvu4uSz78")

flag = True

lock = threading.Lock()

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[2].id)

r = sr.Recognizer()


def output_voice(audio):
        try:
            global flag
            print("hilo creado")
            text = r.recognize_google(audio, language="es-ES")
            print("Has dicho: {}".format(text))
            with lock:
                if text.lower() == "salir":
                        flag = False
                        print("Saliendo...")
                        return
            response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents="Tradúceme esto al inglés: {} , hazlo de una manera informar, y que la respuesta no contenga texto complementario, solo la respuesta".format(text),
            )
            engine.say(response.text)
            engine.runAndWait()
            engine.stop()
                

            print("Traducción: {}".format(response.text))
        except sr.UnknownValueError:
            print("No se pudo entender el audio")
        except sr.RequestError as e:
            print(f"Error al solicitar resultados; {e}")


while flag:
    if not flag:
        break
    with sr.Microphone(device_index=0) as source:
            print("Di algo...")
            audio = r.listen(source) 
            hilo = threading.Thread(target=output_voice, args=(audio,))
            hilo.start()
            
            
    
        

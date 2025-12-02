import queue
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play
import threading
import time
from transformers import AutoTokenizer,VitsModel, AutoModelForSeq2SeqLM
import sounddevice as sd
import numpy as np
from gtts import gTTS
import io
import time
from scipy.io import wavfile
#----------------------------
# Listar dispositivos de audio disponibles
#for i, microphone_name in enumerate(sr.Microphone.list_microphone_names()):
#  print(f"Microphone with name \"{microphone_name}\" found for `Microphone(device_index={i})`")
#----------------------------

# Configuración del modelo de traducción
model_name = "Helsinki-NLP/opus-mt-es-en"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

#Flag de control del bucle principal
flag = True

#Variables para medicion de tiempo
tiempo_inicial = 0
tiempo_final = 0

#Inicializar reconocedor de voz
r = sr.Recognizer()

#Colas y eventos para la comunicación entre hilos
text_tts_queue = queue.Queue()
text_stt_queue = queue.Queue()
stop_event = threading.Event()

#------------------------------------
# Cargar modelo TTS (comentado para usar gTTS)
#tokenizer_tts = AutoTokenizer.from_pretrained("facebook/mms-tts-eng")
#model_tts = VitsModel.from_pretrained("facebook/mms-tts-eng")
#model_tts = model_tts.to("cpu")
#------------------------------------

# Configuración de audio
playback_device = 6


####################

##Worker TTS
def tts_worker():

    print("Hilo TTS iniciado")
    global tiempo_final
    while not stop_event.is_set():
        try:
            text = text_tts_queue.get(timeout=1)
            print(f"Procesando texto para TTS: {text}")

            # Generar audio con gTTS
            audio_wav_buffer = tts_wav(text)
        
            # Normalizar y reproducir audio
            fs_read, audio_normalized = normalized_audio(audio_wav_buffer)
            sd.play(audio_normalized, fs_read, device=playback_device)
            tiempo_final = time.time()
            print(f"Tiempo de respuesta: {tiempo_final - tiempo_inicial} segundos")

            text_tts_queue.task_done()
            print("TTS completado")
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Error en TTS: {e}")


#Normalizar audio
def normalized_audio(audio_wav_buffer):
    fs_read, audio_data = wavfile.read(audio_wav_buffer)
    audio_normalized = audio_data.astype(float) / np.max(np.abs(audio_data))
    return fs_read,audio_normalized


#Generar audio con gTTS
def tts_wav(text):
    tts = gTTS(text=text, lang='en', slow=False)
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    audio = AudioSegment.from_mp3(audio_buffer)
    audio_wav_buffer = io.BytesIO()
    audio.export(audio_wav_buffer, format="wav")
    audio_wav_buffer.seek(0)
    return audio_wav_buffer
   
#Función para procesar voz a texto y traducción
def output_voice(text,r=r,):
    print("Hilo iniciado")
    global flag
    try:
            print("Has dicho: {}".format(text))
            if text.lower() == "salir":
                flag = False
                stop_event.set()
                print("Saliendo...")
                return
            
            inputs = tokenizer(text, return_tensors="pt", padding=True)
            translated = model.generate(**inputs) 
            resultado = tokenizer.decode(translated[0], skip_special_tokens=True)
            text_tts_queue.put(resultado)
            
    except sr.UnknownValueError:
        print("No se pudo entender el audio")


#Función para capturar audio y convertir a texto    
def stt_worker(r):
    while not stop_event.is_set():
        try:
            with sr.Microphone(device_index=1) as source:
                r.adjust_for_ambient_noise(source)
                r.dynamic_energy_threshold = True 
                print("Di algo...")
                audio = r.listen(source,phrase_time_limit=4) 
                text = r.recognize_google(audio, language="es-ES")
                text_stt_queue.put(text)
        except sr.UnknownValueError:
            print("No se pudo entender el audio en el stt_work")
            
        except sr.RequestError as e:
            print(f"Error al solicitar resultados; {e}")

##Run Process
hilo_tts = threading.Thread(target=tts_worker)
hilo_stt = threading.Thread(target=stt_worker, args=(r,))

hilo_tts.start()
hilo_stt.start()


while flag:
    tiempo_inicial = time.time()
    try:
            if not flag:
                break          
            hilo = threading.Thread(target=output_voice, args=(text_stt_queue.get(timeout=1),))
            hilo.start()
            hilo.join()
            text_stt_queue.task_done()
                
                
    except sr.UnknownValueError:
        print("No se pudo entender el audio en el while")
    except sr.RequestError as e:
        print(f"Error al solicitar resultados; {e}")   
    except queue.Empty:
        continue  

print("Fuera del while")  

    
        

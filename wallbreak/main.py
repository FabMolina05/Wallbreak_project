import pyaudio 
import speech_recognition as sr

# Dispositivos de audio disponibles
#m = None
#for i, microphone_name in enumerate(sr.Microphone.list_microphone_names()):
#   print(f"Microphone with name \"{microphone_name}\" found for `Microphone(device_index={i})`")

from google import genai

client = genai.Client(api_key="AIzaSyBEQRCjHyVHg6smwCabwTHz1xJvu4uSz78")



with sr.Microphone(device_index=0) as source:
    r = sr.Recognizer()
    print("Di algo...")
    audio = r.listen(source)
    
    try:
        text = r.recognize_google(audio, language="es-ES")
        print("Has dicho: {}".format(text))
       
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Tradúceme esto al inglés: " + text,
        )

        print("Traducción: {}".format(response.text))
    except sr.UnknownValueError:
        print("No se pudo entender el audio")
    except sr.RequestError as e:
        print("Error al solicitar resultados; {0}".format(e))

    
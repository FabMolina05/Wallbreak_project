from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from google import genai
import time

# Configuración de modelos
model_name = "Helsinki-NLP/opus-mt-es-en"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

client = genai.Client(api_key="AIzaSyBEQRCjHyVHg6smwCabwTHz1xJvu4uSz78")

# Frases de prueba
textos = [
    "Hola, ¿cómo estás?",
    "Me gusta programar en Python",
    "El cielo es azul",
    "Buenos días a todos",
    "¿Qué tiempo hace hoy?"
]

# Prueba Helsinki
print("\nPrueba Helsinki-NLP:")
tiempo_total_helsinki = 0
for texto in textos:
    inicio = time.time()
    inputs = tokenizer(texto, return_tensors="pt", padding=True)
    translated = model.generate(**inputs)
    resultado = tokenizer.decode(translated[0], skip_special_tokens=True)
    fin = time.time()
    tiempo = fin - inicio
    tiempo_total_helsinki += tiempo
    print(f"Texto: {texto}")
    print(f"Traducción: {resultado}")
    print(f"Tiempo: {tiempo:.2f} segundos\n")

# Prueba Gemini
print("\nPrueba Gemini:")
tiempo_total_gemini = 0
for texto in textos:
    inicio = time.time()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Tradúceme esto al inglés: {texto}, hazlo informal y sin texto extra.",
    )
    fin = time.time()
    tiempo = fin - inicio
    tiempo_total_gemini += tiempo
    print(f"Texto: {texto}")
    print(f"Traducción: {response.text}")
    print(f"Tiempo: {tiempo:.2f} segundos\n")

# Resultados finales
print("\nResultados finales:")
print(f"Tiempo promedio Helsinki: {tiempo_total_helsinki/len(textos):.2f} segundos")
print(f"Tiempo promedio Gemini: {tiempo_total_gemini/len(textos):.2f} segundos")
print(f"Tiempo total Helsinki: {tiempo_total_helsinki:.2f} segundos")
print(f"Tiempo total Gemini: {tiempo_total_gemini:.2f} segundos")
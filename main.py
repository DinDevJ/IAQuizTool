from google import genai
from dotenv import load_dotenv
import os
load_dotenv()
# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

def leer_archivo_texto(ruta):
    """Lee el contenido de un archivo de texto y lo devuelve."""
    try:
        # Usamos encoding='utf-8' para no tener problemas con acentos o la 'ñ'
        with open(ruta, 'r', encoding='utf-8') as archivo:
            return archivo.read()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ruta}")
        return ""
# 1. Cargamos el contexto desde tu archivo txt
contexto_sistema = leer_archivo_texto('contexto.txt')

# 2. Definimos la pregunta (más adelante, esto será tu screenshot)
pregunta_usuario = "Un usuario emite un comando ping 2001:db8:face:39::10 y recibe una respuesta que incluye un código 3 . ¿Qué representa este código?"

# 3. Unimos el contexto y la pregunta en un solo texto (Prompt estructurado)
prompt_final = f"""
INSTRUCCIONES DE COMPORTAMIENTO:
{contexto_sistema}

PREGUNTA DEL USUARIO:
{pregunta_usuario}
"""

try:
    print("Analizando la pregunta con el contexto asignado...")
    response = client.models.generate_content(
        model='gemini-3-flash-preview',
        contents=prompt_final
    )
    
    print("\n--- RESPUESTA DE LA IA ---")
    print(response.text)
    print("--------------------------")
    
except Exception as e:
    print(f"Hubo un error al conectar: {e}")
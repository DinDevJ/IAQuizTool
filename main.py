import tkinter as tk
import time
import os
import sys
import threading
from pynput import keyboard
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image
from google import genai
from dotenv import load_dotenv

# --- CONFIGURACIÓN ---
load_dotenv()
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

NOMBRE_CONTEXTO = "contexto.txt"
MODELO = 'gemini-3-flash-preview'
CARPETA_CAPTURAS = r"C:\Users\julio\OneDrive\Pictures\Screenshots"

# --- VARIABLES GLOBALES ---
root = None
texto_ui = None
lbl_estado = None
ventana_visible = True
posicion_izquierda = True # Variable para rastrear de qué lado está

# Constantes de tamaño para poder calcular la posición fácilmente
ANCHO_VENTANA = 320
ALTO_VENTANA = 55

# --- LÓGICA DE IA ---
def leer_contexto(ruta):
    if not os.path.exists(ruta):
        return "Eres un evaluador. Responde solo con la opción correcta."
    with open(ruta, 'r', encoding='utf-8') as archivo:
        return archivo.read()

def actualizar_interfaz(texto):
    global ventana_visible
    texto_ui.config(state='normal')
    texto_ui.delete(1.0, tk.END)
    texto_ui.insert(tk.END, texto)
    texto_ui.config(state='disabled')
    lbl_estado.config(text="● Listo", fg="#888888")
    
    root.deiconify() 
    root.lift()
    ventana_visible = True

def procesar_imagen(ruta_imagen):
    try:
        root.after(0, lambda: lbl_estado.config(text="● Pensando...", fg="#bda55d"))
        root.after(0, lambda: [root.deiconify(), root.lift()])
        global ventana_visible
        ventana_visible = True

        img = None
        intentos = 0
        while intentos < 10:
            try:
                if os.path.getsize(ruta_imagen) > 0:
                    img = Image.open(ruta_imagen)
                    img.load()
                    break
            except Exception:
                pass
            time.sleep(0.5)
            intentos += 1

        if img is None:
            root.after(0, actualizar_interfaz, "Error: Imagen corrupta.")
            return

        contexto_sistema = leer_contexto(NOMBRE_CONTEXTO)
        prompt_texto = f"INSTRUCCIONES:\n{contexto_sistema}\n\nTAREA:\nAnaliza la imagen."
        
        response = client.models.generate_content(
            model=MODELO,
            contents=[prompt_texto, img]
        )
        
        root.after(0, actualizar_interfaz, response.text)
        img.close()

    except Exception as e:
        root.after(0, actualizar_interfaz, f"Error: {e}")

# --- WATCHDOG ---
class ManejadorCapturas(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        ruta_archivo = event.src_path
        if ruta_archivo.lower().endswith(('.png', '.jpg', '.jpeg')) and 'captura de pantalla' in os.path.basename(ruta_archivo).lower():
            threading.Thread(target=procesar_imagen, args=(ruta_archivo,)).start()

# --- INTERFAZ GRÁFICA Y HOTKEYS GLOBALES ---
def ocultar_ventana(evento=None):
    global ventana_visible
    root.withdraw()
    ventana_visible = False

def toggle_ventana():
    global ventana_visible
    if ventana_visible:
        root.withdraw()
        ventana_visible = False
    else:
        root.deiconify()
        root.lift()
        ventana_visible = True

def mover_ventana():
    """Calcula el ancho de la pantalla y alterna la posición del recuadro."""
    global posicion_izquierda
    pantalla_ancho = root.winfo_screenwidth()
    pantalla_alto = root.winfo_screenheight()
    
    y = pantalla_alto - ALTO_VENTANA - 50 
    
    if posicion_izquierda:
        # Si está a la izquierda, lo mandamos a la derecha
        # Posición X = Ancho total - Ancho de ventana - Margen de 20px
        x = pantalla_ancho - ANCHO_VENTANA - 20
        posicion_izquierda = False
    else:
        # Si está a la derecha, lo regresamos a la izquierda
        x = 20
        posicion_izquierda = True
        
    root.geometry(f"{ANCHO_VENTANA}x{ALTO_VENTANA}+{x}+{y}")

# --- Wrappers para pynput ---
def on_hotkey_toggle():
    root.after(0, toggle_ventana)

def on_hotkey_hide():
    root.after(0, ocultar_ventana)

def on_hotkey_move():
    root.after(0, mover_ventana)

def cerrar_aplicacion():
    observer.stop()
    observer.join()
    if 'hotkey_listener' in globals():
        hotkey_listener.stop()
    root.quit()

def iniciar_interfaz():
    global root, texto_ui, lbl_estado
    
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes('-topmost', True)
    root.configure(bg='#181818')
    
    # Inicia por defecto a la izquierda
    x = 20
    y = root.winfo_screenheight() - ALTO_VENTANA - 50 
    root.geometry(f"{ANCHO_VENTANA}x{ALTO_VENTANA}+{x}+{y}")
    
    frame_top = tk.Frame(root, bg='#121212', height=14)
    frame_top.pack(fill='x')
    frame_top.pack_propagate(False)
    
    lbl_estado = tk.Label(frame_top, text="● Esperando", bg='#121212', fg='#555555', font=('Arial', 7))
    lbl_estado.pack(side='left', padx=5)
    
    btn_cerrar = tk.Button(frame_top, text="✕", command=cerrar_aplicacion, bg='#121212', fg='#666666', activebackground='#c62828', activeforeground='white', relief='flat', bd=0, font=('Arial', 7), cursor="hand2")
    btn_cerrar.pack(side='right', padx=5)
    
    texto_ui = tk.Text(root, bg='#181818', fg='#cccccc', font=('Consolas', 9), wrap='word', bd=0, padx=8, pady=4)
    texto_ui.insert(tk.END, "Esperando captura...")
    texto_ui.config(state='disabled')
    texto_ui.pack(expand=True, fill='both')
    
    texto_ui.bind('<Double-Button-1>', ocultar_ventana)
    
    root.mainloop()

# --- INICIO ---
if __name__ == "__main__":
    observer = Observer()
    observer.schedule(ManejadorCapturas(), CARPETA_CAPTURAS, recursive=False)
    observer.start()
    
    atajos = {
        '<ctrl>+<alt>+v': on_hotkey_toggle,
        '<esc>': on_hotkey_hide,
        '<ctrl>+<alt>+m': on_hotkey_move # ¡Nuevo atajo para mover!
    }
    hotkey_listener = keyboard.GlobalHotKeys(atajos)
    hotkey_listener.start()
    
    iniciar_interfaz()
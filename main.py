import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import time
import os
import sys
import json
import threading
from pynput import keyboard, mouse as pmouse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image, ImageGrab
from google import genai

if sys.platform == 'win32':
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

# --- CONFIGURACIÓN ---
CONFIG_FILE = "config.json"
NOMBRE_CONTEXTO = "contexto.txt"
MODELO = 'gemini-3-flash-preview'

ANCHO_VENTANA = 320
ALTO_VENTANA = 55

# --- VARIABLES GLOBALES ---
root = None
texto_ui = None
lbl_estado = None
ventana_visible = True
posicion_izquierda = True
captura_en_curso = False
chat_ventana = None

# --- CONFIG PERSISTENTE ---
def get_app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_config_path():
    return os.path.join(get_app_dir(), CONFIG_FILE)

def cargar_config():
    path = get_config_path()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}

def guardar_config(config):
    with open(get_config_path(), 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

def configuracion_inicial(config):
    setup_root = tk.Tk()
    setup_root.withdraw()

    if not config.get('gemini_api_key'):
        api_key = simpledialog.askstring(
            "Configuración inicial - IAQuizTool",
            "Ingresa tu Gemini API Key:",
            show='*',
            parent=setup_root,
        )
        if not api_key or not api_key.strip():
            messagebox.showerror("Error", "API Key requerida. Cerrando.")
            setup_root.destroy()
            sys.exit(1)
        config['gemini_api_key'] = api_key.strip()

    if not config.get('screenshots_folder') or not os.path.isdir(config['screenshots_folder']):
        initial = os.path.expanduser("~/Pictures/Screenshots")
        if not os.path.isdir(initial):
            initial = os.path.expanduser("~")
        messagebox.showinfo(
            "Configuración inicial - IAQuizTool",
            "Ahora selecciona la carpeta donde se guardan tus capturas de pantalla.",
            parent=setup_root,
        )
        folder = filedialog.askdirectory(
            title="Selecciona tu carpeta de capturas de pantalla",
            initialdir=initial,
            parent=setup_root,
        )
        if not folder:
            messagebox.showerror("Error", "Carpeta requerida. Cerrando.")
            setup_root.destroy()
            sys.exit(1)
        config['screenshots_folder'] = folder

    guardar_config(config)
    setup_root.destroy()
    return config

config = cargar_config()
if not config.get('gemini_api_key') or not config.get('screenshots_folder'):
    config = configuracion_inicial(config)

client = genai.Client(api_key=config['gemini_api_key'])
CARPETA_CAPTURAS = config['screenshots_folder']

# --- LÓGICA DE IA ---
def leer_contexto(ruta):
    ruta_absoluta = ruta if os.path.isabs(ruta) else os.path.join(get_app_dir(), ruta)
    if not os.path.exists(ruta_absoluta):
        return "Eres un evaluador. Responde solo con la opción correcta."
    with open(ruta_absoluta, 'r', encoding='utf-8') as archivo:
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
        img.close()
        try:
            os.remove(ruta_imagen)
        except OSError:
            pass
        root.after(0, actualizar_interfaz, response.text)

    except Exception as e:
        root.after(0, actualizar_interfaz, f"Error: {e}")

def procesar_pregunta_texto(pregunta):
    try:
        root.after(0, lambda: lbl_estado.config(text="● Pensando...", fg="#bda55d"))
        root.after(0, lambda: [root.deiconify(), root.lift()])
        global ventana_visible
        ventana_visible = True

        contexto_sistema = leer_contexto(NOMBRE_CONTEXTO)
        prompt_texto = f"INSTRUCCIONES:\n{contexto_sistema}\n\nPREGUNTA:\n{pregunta}"

        response = client.models.generate_content(
            model=MODELO,
            contents=[prompt_texto]
        )
        root.after(0, actualizar_interfaz, response.text)
    except Exception as e:
        root.after(0, actualizar_interfaz, f"Error: {e}")

# --- CHAT (entrada por texto) ---
ANCHO_CHAT = 420
ALTO_CHAT = 170

def posicion_chat():
    pantalla_ancho = root.winfo_screenwidth()
    pantalla_alto = root.winfo_screenheight()
    y = pantalla_alto - ALTO_CHAT - 50
    if posicion_izquierda:
        x = pantalla_ancho - ANCHO_CHAT - 20
    else:
        x = 20
    return x, y

def abrir_chat():
    global chat_ventana
    if chat_ventana is not None:
        chat_ventana.deiconify()
        chat_ventana.lift()
        return

    dialogo = tk.Toplevel(root)
    dialogo.overrideredirect(True)
    dialogo.attributes('-topmost', True)
    dialogo.configure(bg='#181818')

    x, y = posicion_chat()
    dialogo.geometry(f"{ANCHO_CHAT}x{ALTO_CHAT}+{x}+{y}")
    chat_ventana = dialogo

    header = tk.Frame(dialogo, bg='#121212', height=16, cursor='fleur')
    header.pack(fill='x')
    header.pack_propagate(False)

    lbl_titulo = tk.Label(header, text="Pregunta a IA  (Enter envía · Esc cierra)",
                          bg='#121212', fg='#888888', font=('Arial', 7), cursor='fleur')
    lbl_titulo.pack(side='left', padx=6)

    def cerrar():
        global chat_ventana
        chat_ventana = None
        dialogo.destroy()

    btn_cerrar = tk.Button(header, text="✕", command=cerrar,
                           bg='#121212', fg='#666666', activebackground='#c62828',
                           activeforeground='white', relief='flat', bd=0,
                           font=('Arial', 7), cursor='hand2')
    btn_cerrar.pack(side='right', padx=4)

    drag_offset = {'x': 0, 'y': 0}

    def start_drag(event):
        drag_offset['x'] = event.x_root - dialogo.winfo_x()
        drag_offset['y'] = event.y_root - dialogo.winfo_y()

    def do_drag(event):
        nx = event.x_root - drag_offset['x']
        ny = event.y_root - drag_offset['y']
        dialogo.geometry(f"+{nx}+{ny}")

    for w in (header, lbl_titulo):
        w.bind('<ButtonPress-1>', start_drag)
        w.bind('<B1-Motion>', do_drag)

    text_widget = tk.Text(dialogo, bg='#222222', fg='#ffffff', insertbackground='#ffffff',
                          font=('Consolas', 10), wrap='word', bd=0, height=5, padx=6, pady=4)
    text_widget.pack(fill='both', expand=True, padx=6, pady=(2, 6))
    text_widget.focus_force()

    def enviar(event=None):
        pregunta = text_widget.get('1.0', 'end').strip()
        if not pregunta:
            return 'break'
        cerrar()
        threading.Thread(target=procesar_pregunta_texto, args=(pregunta,), daemon=True).start()
        return 'break'

    text_widget.bind('<Return>', enviar)
    dialogo.bind('<Escape>', lambda e: cerrar())
    dialogo.protocol('WM_DELETE_WINDOW', cerrar)

# --- CAPTURA DE REGIÓN DISCRETA ---
COLOR_TRANSPARENTE = '#ff00ff'

def iniciar_captura_region():
    global captura_en_curso
    if captura_en_curso:
        return
    captura_en_curso = True

    overlay = tk.Toplevel(root)
    overlay.attributes('-fullscreen', True)
    overlay.attributes('-topmost', True)
    overlay.attributes('-transparentcolor', COLOR_TRANSPARENTE)
    overlay.configure(bg=COLOR_TRANSPARENTE)

    canvas = tk.Canvas(overlay, bg=COLOR_TRANSPARENTE, highlightthickness=0, bd=0)
    canvas.pack(fill='both', expand=True)

    state = {
        'start_x': None, 'start_y': None,
        'rect_id': None, 'listener': None,
    }

    def cerrar_overlay():
        global captura_en_curso
        captura_en_curso = False
        if state['listener'] is not None:
            try:
                state['listener'].stop()
            except Exception:
                pass
        overlay.destroy()

    def crear_rect(x, y):
        if state['rect_id'] is not None:
            canvas.delete(state['rect_id'])
        state['rect_id'] = canvas.create_rectangle(
            x, y, x, y,
            outline='black', width=1, fill=COLOR_TRANSPARENTE
        )

    def actualizar_rect(x, y):
        if state['rect_id'] is not None:
            canvas.coords(state['rect_id'],
                          state['start_x'], state['start_y'], x, y)

    def finalizar(x1, y1, x2, y2):
        cerrar_overlay()
        left, right = sorted([x1, x2])
        top, bottom = sorted([y1, y2])
        if right - left < 5 or bottom - top < 5:
            return
        root.after(80, lambda: capturar_region(left, top, right, bottom))

    def capturar_region(left, top, right, bottom):
        try:
            img = ImageGrab.grab(bbox=(left, top, right, bottom))
            ruta = os.path.join(CARPETA_CAPTURAS, f"iaqt_{int(time.time()*1000)}.png")
            img.save(ruta, 'PNG')
        except Exception as e:
            root.after(0, actualizar_interfaz, f"Error al capturar región: {e}")

    def on_mouse_click(x, y, button, pressed):
        if button != pmouse.Button.left:
            return
        if pressed:
            state['start_x'] = x
            state['start_y'] = y
            root.after(0, crear_rect, x, y)
        else:
            if state['start_x'] is None:
                return
            x1, y1 = state['start_x'], state['start_y']
            root.after(0, finalizar, x1, y1, x, y)
            return False

    def on_mouse_move(x, y):
        if state['start_x'] is not None and state['rect_id'] is not None:
            root.after(0, actualizar_rect, x, y)

    overlay.bind('<Escape>', lambda e: cerrar_overlay())
    overlay.focus_force()

    state['listener'] = pmouse.Listener(on_click=on_mouse_click, on_move=on_mouse_move)
    state['listener'].start()

# --- WATCHDOG ---
class ManejadorCapturas(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        ruta_archivo = event.src_path
        if ruta_archivo.lower().endswith(('.png', '.jpg', '.jpeg')):
            threading.Thread(target=procesar_imagen, args=(ruta_archivo,), daemon=True).start()

# --- INTERFAZ GRÁFICA Y HOTKEYS GLOBALES ---
def ocultar_ventana(evento=None):
    global ventana_visible
    root.withdraw()
    if chat_ventana is not None:
        chat_ventana.withdraw()
    ventana_visible = False

def toggle_ventana():
    global ventana_visible
    if ventana_visible:
        root.withdraw()
        if chat_ventana is not None:
            chat_ventana.withdraw()
        ventana_visible = False
    else:
        root.deiconify()
        root.lift()
        if chat_ventana is not None:
            chat_ventana.deiconify()
            chat_ventana.lift()
        ventana_visible = True

def mover_ventana():
    """Calcula el ancho de la pantalla y alterna la posición del recuadro."""
    global posicion_izquierda
    pantalla_ancho = root.winfo_screenwidth()
    pantalla_alto = root.winfo_screenheight()

    y = pantalla_alto - ALTO_VENTANA - 50

    if posicion_izquierda:
        x = pantalla_ancho - ANCHO_VENTANA - 20
        posicion_izquierda = False
    else:
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

def on_hotkey_chat():
    root.after(0, abrir_chat)

def on_hotkey_capturar():
    root.after(0, iniciar_captura_region)

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
        '<ctrl>+<alt>+m': on_hotkey_move,
        '<ctrl>+<alt>+t': on_hotkey_chat,
        '<ctrl>+<alt>+s': on_hotkey_capturar
    }
    hotkey_listener = keyboard.GlobalHotKeys(atajos)
    hotkey_listener.start()

    iniciar_interfaz()

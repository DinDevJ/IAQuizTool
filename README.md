# 👁️ IAQuizTool (Powered by Gemini Vision)

Un asistente de escritorio minimalista, invisible y en tiempo real.
Convierte cualquier zona de tu pantalla en un _prompt_ instantáneo para la IA multimodal de Google Gemini, sin necesidad de abrir el navegador, cambiar de pestañas o arrastrar imágenes.

Ideal para programadores analizando código, estudiantes resolviendo problemas visuales, o cualquier persona que necesite explicaciones rápidas sobre lo que está viendo en su monitor.

## Características Principales

- **Flujo sin fricción:** Usa la herramienta de recortes nativa de tu sistema operativo. El asistente detecta automáticamente la nueva imagen y la procesa.
- **Interfaz Flotante Minimalista:** Un pequeño recuadro sin bordes que aparece sobre todas tus ventanas solo cuando lo necesitas, y se oculta cuando pierde el foco.
- **Contexto Personalizable:** Define la "personalidad" o el rol de la IA mediante un simple archivo de texto.
- **Atajos Globales (Hotkeys):** Control total sin usar el mouse.
- **Cero Costo:** Utiliza la capa gratuita de Google AI Studio (Gemini 2.0 / 3.0 Flash).

## ¿Cómo funciona?

El script opera en segundo plano (modo fantasma).

1. Utiliza la librería `watchdog` para vigilar tu carpeta de Capturas de Pantalla.
2. Cuando realizas un recorte (ej. `Win + Shift + S`), el script detecta el nuevo archivo.
3. Lee tus instrucciones desde `contexto.txt` y envía la imagen a Gemini mediante la API oficial `google-genai`.
4. Muestra la respuesta en una ventana de `Tkinter` ultra-discreta que puedes mover o esconder con el teclado.
5. Con Ctrl+M lo puedes mover de izquierda a derecha o biceversa
6. [Esc] Lo escondes
7. Ctrl+Alt+V Lo vuelves a mostrar

---

## ⚙️ Instalación y Configuración

### 1. Clonar el repositorio e instalar dependencias

Asegúrate de tener Python 3.x instalado. Abre tu terminal y ejecuta:

```bash
git clone https://github.com/DinDevJ/IAQuizTool.git
cd IAQuizTool
pip install -r requirements.txt
```

### 2. Compilar a .exe (opcional)

Ejecuta el script de build incluido. Instalará PyInstaller si hace falta y generará el ejecutable:

```bash
build.bat
```

El `.exe` quedará en `dist\IAQuizTool.exe`.

### 3. Primer uso

La primera vez que ejecutes el programa (script o .exe) aparecerán dos diálogos:

1. **Gemini API Key** — pega tu clave de Google AI Studio.
2. **Carpeta de capturas** — selecciona la carpeta donde Windows guarda tus screenshots (normalmente `C:\Users\TU_USUARIO\Pictures\Screenshots`).

Ambos valores quedan guardados en `config.json` junto al ejecutable, así que solo te lo pregunta una vez. Si quieres reconfigurarlo, elimina ese archivo.

### Estructura de archivos recomendada

```text
📁 Mi_Asistente_IA/
├── 📄 config.json        # Generado automáticamente en el primer uso
├── 📄 contexto.txt       # (Opcional) Instrucciones personalizadas para la IA
└── 🚀 IAQuizTool.exe     # El ejecutable
```

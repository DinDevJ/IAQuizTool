# 👁️ IAQuizTool (Powered by Gemini Vision)

Un asistente de escritorio minimalista, invisible y en tiempo real. 
Convierte cualquier zona de tu pantalla en un *prompt* instantáneo para la IA multimodal de Google Gemini, sin necesidad de abrir el navegador, cambiar de pestañas o arrastrar imágenes.

Ideal para programadores analizando código, estudiantes resolviendo problemas visuales, o cualquier persona que necesite explicaciones rápidas sobre lo que está viendo en su monitor.

## Características Principales

* **Flujo sin fricción:** Usa la herramienta de recortes nativa de tu sistema operativo. El asistente detecta automáticamente la nueva imagen y la procesa.
* **Interfaz Flotante Minimalista:** Un pequeño recuadro sin bordes que aparece sobre todas tus ventanas solo cuando lo necesitas, y se oculta cuando pierde el foco.
* **Contexto Personalizable:** Define la "personalidad" o el rol de la IA mediante un simple archivo de texto.
* **Atajos Globales (Hotkeys):** Control total sin usar el mouse.
* **Cero Costo:** Utiliza la capa gratuita de Google AI Studio (Gemini 2.0 / 3.0 Flash).

## ¿Cómo funciona?

El script opera en segundo plano (modo fantasma). 
1. Utiliza la librería `watchdog` para vigilar tu carpeta de Capturas de Pantalla.
2. Cuando realizas un recorte (ej. `Win + Shift + S`), el script detecta el nuevo archivo.
3. Lee tus instrucciones desde `contexto.txt` y envía la imagen a Gemini mediante la API oficial `google-genai`.
4. Muestra la respuesta en una ventana de `Tkinter` ultra-discreta que puedes mover o esconder con el teclado.

---

## ⚙️ Instalación y Configuración

### 1. Clonar el repositorio e instalar dependencias
Asegúrate de tener Python 3.x instalado. Abre tu terminal y ejecuta:
```bash
git clone [https://github.com/tu-usuario/tu-repositorio.git](https://github.com/tu-usuario/tu-repositorio.git)
cd tu-repositorio
pip install -r requirements.txt


### ⚠️ Importante: Estructura de archivos post-compilación

Una vez generado tu programa (lo encontrarás dentro de la carpeta `dist`), es **estrictamente necesario** que lo saques de ahí y lo coloques en una nueva carpeta junto con tus archivos de configuración. 

Tu carpeta final de uso diario debe verse exactamente así:

```text
📁 Mi_Asistente_IA/
├── 📄 .env               # Contiene tu GEMINI_API_KEY
├── 📄 contexto.txt       # Contiene tus instrucciones para la IA
└── 🚀 main.exe           # El ejecutable que acabas de compilar
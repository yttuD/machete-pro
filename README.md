# Machete Pro: AI Meeting Assistant 🤖🎙️

Este es un asistente de IA impulsado por la voz que escucha en tiempo real el micrófono o el audio del sistema (Loopback WASAPI) y utiliza una arquitectura RAG (Retrieval-Augmented Generation) para responder basándose en una base de conocimientos en Markdown y PDF.

## ⚙️ Arquitectura del Sistema
El proyecto combina tres tecnologías locales principales:
1. **ASR (Reconocimiento Automático de Voz):** `faster-whisper` (Modelo Medium) y `silero-vad` para el control de silencios y detección de voz.
2. **RAG (Recuperación de Información):** `FAISS` (Indexación vectorial) y `sentence-transformers` (paraphrase-multilingual-MiniLM-L12-v2) para buscar en el documento `Todo BDD/master.md`.
3. **LLM (Modelo de Lenguaje Local):** `LM Studio` corriendo el modelo `qwen2.5-coder-7b-instruct` para estructurar y dar respuestas conversacionales inteligentes.

---

## 🛠️ Requisitos Previos e Instalación

Para que una IA o un humano despliegue este software en una computadora nueva desde cero, seguir los siguientes pasos:

### 1. Dependencias del Sistema
- Python 3.10 o superior (Probado en Python 3.13)
- Tarjeta Gráfica (GPU) con soporte CUDA (recomendado para Faster-Whisper)
- Instalar **LM Studio** localmente en la máquina.

### 2. Librerías de Python
Ejecutar el siguiente comando para instalar las librerías necesarias:

```bash
pip install PyQt6 soundcard faster-whisper torch torchaudio faiss-cpu sentence-transformers keyboard requests numpy
```
> **Nota:** La librería `soundcard` se usa en lugar de `sounddevice` para evitar errores nativos de PortAudio con micrófonos Loopback WASAPI en Windows, permitiendo captura nativa de escritorio y auto-resampling de canales estéreo.

---

## 🚀 Guía de Inicio

### Paso 1: Configurar el LLM
1. Abre **LM Studio**.
2. Descarga el modelo `qwen2.5-coder-7b-instruct` (o configura el código en `main_ui.py` para tu modelo preferido).
3. Asegúrate de que el servidor local de desarrollo (Local Inference Server) esté configurado en el puerto `1234`. La interfaz iniciará el servidor mediante comandos (`lms server start`) automáticamente al abrir el programa.

### Paso 2: Generar la Base de Conocimiento (FAISS)
Antes de usar la aplicación por primera vez o después de actualizar `master.md`:
```bash
cd AI_Assistant
python build_index.py
```
Esto creará una carpeta `index_data` conteniendo los vectores y metadatos extraídos de tus apuntes.

### Paso 3: Ejecutar la Interfaz de Usuario
```bash
cd AI_Assistant
python main_ui.py
```
*(Opcional: Ejecutar `Iniciar_Asistente.bat` en Windows)*

---

## 🔧 Configuración Avanzada y Trucos para la IA
- **Loopback de Audio:** Si el usuario quiere capturar el audio de una entrevista por Zoom/Meet, debe seleccionar en el menú desplegable de la UI el dispositivo marcado con **`🔊 [Loopback]`** (Ej: sus propios auriculares). El código de `soundcard` se encarga de aislar el audio estéreo, convertirlo a mono y remuestrearlo a 16kHz para Whisper automáticamente.
- **Hotwords:** Whisper suele confundir acrónimos (ej: SQL como "seguele", o ACID). Para evitar esto, en `main_ui.py` hay una variable `self.hotwords` cargada explícitamente con el vocabulario técnico de bases de datos. Si se detectan más fallos de entendimiento (Ej: "tomosidad"), deben añadirse a esa variable o crear una capa de corrección fonética en código.
- **VAD Preroll Buffer:** Se incluye un búfer circular (pre-roll) manual para evitar que Whisper se coma el primer medio segundo del audio al empezar a hablar.

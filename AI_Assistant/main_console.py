import threading
import queue
import time
import requests
import json
import torch
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
import faiss
import pickle
from sentence_transformers import SentenceTransformer
import warnings
import os
import sys

warnings.filterwarnings("ignore")

CONFIG_FILE = "config.json"
LLM_ENDPOINT = "http://localhost:1234/v1/chat/completions"
LLM_MODEL = "qwen2.5-coder-7b-instruct"

# Colas y banderas para sincronización de hilos
text_queue = queue.Queue()
interruption_flag = threading.Event()

def load_knowledge_base():
    print("[*] Cargando índice RAG...")
    try:
        index = faiss.read_index("index_data/faiss_index.bin")
        with open("index_data/documents.pkl", "rb") as f:
            documents = pickle.load(f)
            
        # Generar initial_prompt dinámico para Whisper basado en los títulos
        titles = [doc["title"] for doc in documents]
        dynamic_prompt = "Clase sobre bases de datos: "
        for title in titles:
            if len(dynamic_prompt) + len(title) > 800:
                break
            dynamic_prompt += title + ", "
        dynamic_prompt = dynamic_prompt.strip(", ")
        os.environ["WHISPER_PROMPT"] = dynamic_prompt
        
        emb_model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        return index, documents, emb_model
    except Exception as e:
        print(f"Error cargando FAISS: {e}\nAsegúrate de haber ejecutado build_index.py primero.")
        sys.exit(1)

def get_context(query, index, documents, emb_model):
    q_emb = emb_model.encode([query]).astype("float32")
    D, I = index.search(q_emb, k=2) # Traer los 2 conceptos más relevantes
    context = ""
    for i in range(len(I[0])):
        idx = I[0][i]
        context += documents[idx]['content'] + "\n\n"
    return context

def llm_worker(index, documents, emb_model):
    """Hilo encargado de recibir transcripciones, buscar contexto y hablar con el LLM"""
    while True:
        text = text_queue.get()
        if text is None:
            break
            
        context = get_context(text, index, documents, emb_model)
        prompt = f"Contexto recuperado:\n{context}\nUsuario dijo: {text}"
        
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": "Sos un asistente de reuniones. Responde de forma ultra concisa basándote SÓLO en el contexto recuperado. Si no está en el contexto, dilo."},
                {"role": "user", "content": prompt}
            ],
            "stream": True,
            "temperature": 0.1
        }
        
        print("\n\033[96m[Asistente]: \033[0m", end="", flush=True)
        interruption_flag.clear()
        
        try:
            with requests.post(LLM_ENDPOINT, json=payload, headers=headers, stream=True) as response:
                if response.status_code == 200:
                    for line in response.iter_lines():
                        if interruption_flag.is_set():
                            print("\033[91m [INTERRUMPIDO]\033[0m")
                            break
                            
                        if line:
                            decoded_line = line.decode('utf-8')
                            if decoded_line.startswith("data: "):
                                data_str = decoded_line[6:]
                                if data_str == "[DONE]":
                                    break
                                try:
                                    data = json.loads(data_str)
                                    if "choices" in data and len(data["choices"]) > 0:
                                        delta = data["choices"][0].get("delta", {})
                                        content = delta.get("content", "")
                                        if content:
                                            print(content, end="", flush=True)
                                except json.JSONDecodeError:
                                    pass
                else:
                    print(f"Error {response.status_code} - Revisa el servidor LM Studio.")
            if not interruption_flag.is_set():
                print("\n\n\033[90m[Escuchando...]\033[0m")
        except requests.exceptions.ConnectionError:
            print("\033[91m[Error: Servidor LLM apagado]\033[0m")
            
        text_queue.task_done()

def main():
    print("=== Fase 4: Integración Pipeline End-to-End ===")
    
    if not os.path.exists(CONFIG_FILE):
        print("Falta config.json. Corre test_audio_pipeline.py primero para seleccionar el micrófono.")
        sys.exit(1)
        
    with open(CONFIG_FILE, "r") as f:
        device_id = json.load(f).get("device_index")
        
    index, documents, emb_model = load_knowledge_base()
    
    print("[*] Cargando VAD y Whisper...")
    vad_model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=False, trust_repo=True)
    whisper_model = WhisperModel("small", device="cuda", compute_type="float16")
    
    # Iniciar hilo del LLM
    llm_t = threading.Thread(target=llm_worker, args=(index, documents, emb_model), daemon=True)
    llm_t.start()
    
    SAMPLE_RATE = 16000
    CHUNK_SIZE = 512 # Silero exige exactamente 512 muestras a 16000Hz (32ms)
    
    raw_audio_queue = queue.Queue()
    
    def audio_callback(indata, frames, time_info, status):
        # Callback bloquea el hilo de audio si tarda mucho, solo metemos a la cola
        mono_data = indata.mean(axis=1)
        raw_audio_queue.put(mono_data)

    print("\n\033[92m[!] Todo listo. Sistema ESCUCHANDO en tiempo real. Presiona Ctrl+C para salir.\033[0m")
    print("\033[90m[Escuchando...]\033[0m")
    
    audio_buffer = []
    is_speaking = False
    silence_counter = 0
    SILENCE_CHUNKS_THRESHOLD = 24 # 24 chunks de 32ms = ~768ms de silencio para dar fin al turno
    
    # Usamos try/except para manejar Ctrl+C limpio
    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, blocksize=CHUNK_SIZE, device=device_id, channels=1, callback=audio_callback):
            while True:
                chunk = raw_audio_queue.get()
                audio_tensor = torch.from_numpy(chunk.astype(np.float32))
                
                # Cálculo de VAD para el chunk
                speech_prob = vad_model(audio_tensor, SAMPLE_RATE).item()
                
                if speech_prob > 0.5:
                    if not is_speaking:
                        is_speaking = True
                        interruption_flag.set() # POLÍTICA DE INTERRUPCIÓN: pisar el LLM
                        audio_buffer = []
                        print("\r\033[93m[🎤 Capturando voz...]  \033[0m", end="", flush=True)
                    silence_counter = 0
                    audio_buffer.extend(chunk.tolist())
                else:
                    if is_speaking:
                        audio_buffer.extend(chunk.tolist())
                        silence_counter += 1
                        
                        if silence_counter >= SILENCE_CHUNKS_THRESHOLD:
                            is_speaking = False
                            print("\r\033[90m[Procesando audio...]\033[0m", end="", flush=True)
                            
                            speech_audio = np.array(audio_buffer, dtype=np.float32)
                            
                            # Transcribir en bloque 
                            dyn_prompt = os.environ.get("WHISPER_PROMPT", "Clase sobre bases de datos")
                            segments, _ = whisper_model.transcribe(speech_audio, beam_size=5, language="es", initial_prompt=dyn_prompt)
                            text = "".join([s.text for s in segments]).strip()
                            
                            if len(text) > 3: # Filtro de ruido
                                print(f"\r\n\033[95m[Usuario]:\033[0m {text}")
                                text_queue.put(text)
                            else:
                                print("\r\033[90m[Escuchando...]      \033[0m", end="", flush=True)
    except KeyboardInterrupt:
        print("\nSaliendo...")

if __name__ == "__main__":
    import os
    os.system('color') # Habilitar colores ANSI en terminales de Windows antiguas
    main()

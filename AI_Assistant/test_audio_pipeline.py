import time
import torch
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
import json
import os
import warnings
import pickle

warnings.filterwarnings("ignore")

CONFIG_FILE = "config.json"

def get_dynamic_prompt():
    try:
        with open("index_data/documents.pkl", "rb") as f:
            documents = pickle.load(f)
        titles = [doc["title"] for doc in documents]
        prompt = "Clase sobre bases de datos: "
        for title in titles:
            # Limitamos a unos ~200 tokens aprox (aprox 800 caracteres para estar seguros)
            if len(prompt) + len(title) > 800:
                break
            prompt += title + ", "
        return prompt.strip(", ")
    except Exception:
        return "Clase sobre bases de datos, tecnología, audio"


def select_audio_device():
    devices = sd.query_devices()
    print("\n--- Dispositivos Disponibles ---")
    valid_devices = []
    for i, dev in enumerate(devices):
        try:
            hostapi = sd.query_hostapis(dev['hostapi'])
            if "WASAPI" in hostapi['name'] or "MME" in hostapi['name']:
                print(f"[{i}] {dev['name']} (In: {dev['max_input_channels']})")
                valid_devices.append(i)
        except Exception:
            pass
            
    while True:
        try:
            choice = input("\nIngresa el ID de tu MICRÓFONO para esta prueba (no loopback, un micrófono real para hablar ahora): ")
            choice = int(choice)
            if choice in valid_devices:
                with open(CONFIG_FILE, "w") as f:
                    json.dump({"device_index": choice}, f)
                return choice
            else:
                print("ID no válido.")
        except ValueError:
            print("Por favor, ingresa un número.")

def main():
    if not os.path.exists(CONFIG_FILE):
        device_id = select_audio_device()
    else:
        with open(CONFIG_FILE, "r") as f:
            device_id = json.load(f).get("device_index")
            if device_id is None:
                device_id = select_audio_device()
            
    print("\nCargando VAD (Silero)...")
    vad_model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=False, trust_repo=True)
    get_speech_timestamps = utils[0]
    
    print("Cargando Faster-Whisper (small, CUDA)...")
    # Usa fp16 en GPU. Requerirá ~1-1.5 GB de VRAM.
    whisper_model = WhisperModel("small", device="cuda", compute_type="float16")
    
    SAMPLE_RATE = 16000
    print(f"\n[*] Todo listo. Grabando del dispositivo {device_id}...")
    print("\n>>> POR FAVOR, HABLA UNA ORACIÓN CORTA Y LUEGO HAZ SILENCIO <<<")
    
    # Grabamos 5 segundos para simplificar la prueba y medir los tiempos de procesamiento post-grabación.
    duration = 5
    audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, device=device_id, dtype='float32')
    sd.wait()
    print("Grabación terminada. Procesando métricas...\n")
    
    audio_tensor = torch.from_numpy(audio.flatten())
    
    # 1. Medir VAD
    vad_start_time = time.time()
    # Usamos los parámetros por defecto de Silero, que usualmente toman chunks de 512 samples
    timestamps = get_speech_timestamps(audio_tensor, vad_model, sampling_rate=SAMPLE_RATE)
    vad_end_time = time.time()
    vad_latency = vad_end_time - vad_start_time
    
    if not timestamps:
        print("VAD no detectó voz en el audio grabado.")
        return
        
    print(f"[*] Tiempo de procesamiento VAD (Silero): {vad_latency:.3f} segundos")
    
    # Recortamos el audio al segmento con voz
    start_sample = timestamps[0]['start']
    end_sample = timestamps[-1]['end']
    speech_audio = audio.flatten()[start_sample:end_sample]
    
    # 2. Medir Transcripción
    transcription_start_time = time.time()
    # Beam size = 5 es un buen balance entre velocidad y precisión
    dynamic_prompt = get_dynamic_prompt()
    print(f"[*] Usando initial_prompt ({len(dynamic_prompt)} chars): {dynamic_prompt[:80]}...")
    segments, info = whisper_model.transcribe(speech_audio, beam_size=5, language="es", initial_prompt=dynamic_prompt)
    text = "".join([segment.text for segment in segments])
    transcription_end_time = time.time()
    whisper_latency = transcription_end_time - transcription_start_time
    
    print(f"[*] Tiempo de Transcripción (Faster-Whisper): {whisper_latency:.3f} segundos")
    print(f"[*] Tiempo Total de Pipeline de Audio (VAD + Whisper): {vad_latency + whisper_latency:.3f} segundos")
    
    print(f"\nTexto reconocido:\n> {text.strip()}")
    
    print("\n[*] Fase 3 completada.")

if __name__ == "__main__":
    main()

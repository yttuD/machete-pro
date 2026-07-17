import time
import pickle
import faiss
import os
from faster_whisper import WhisperModel

def get_dynamic_prompt():
    try:
        if os.path.exists("index_data/documents.pkl"):
            with open("index_data/documents.pkl", "rb") as f:
                documents = pickle.load(f)
            
            # Recolectar títulos para el prompt (evita alucinaciones de vocabulario)
            titulos = []
            for doc in documents:
                title = doc["title"].replace("## ", "").strip()
                if title and title not in titulos:
                    titulos.append(title)
            
            # Limitar a 250 caracteres para no exceder los 224 tokens de Whisper (evita Error position >= 448)
            prompt = "Clase sobre bases de datos: " + ", ".join(titulos)
            return prompt[:250] 
    except Exception as e:
        print(f"Error cargando contexto: {e}")
    return "Clase de informática, bases de datos, sql, nosql, teoria de bases de datos."

def main():
    audio_file = "test_class.wav"
    if not os.path.exists(audio_file):
        print(f"Error: {audio_file} no encontrado.")
        return

    print("Cargando modelo Faster-Whisper (medium)...")
    model = WhisperModel("medium", device="cuda", compute_type="float16")
    
    dynamic_prompt = get_dynamic_prompt()
    print(f"Usando initial_prompt: {dynamic_prompt[:100]}...")
    
    print(f"Transcribiendo {audio_file}...")
    start_time = time.time()
    
    segments, info = model.transcribe(
        audio_file, 
        beam_size=5, 
        language="es",
        initial_prompt=dynamic_prompt,
        hotwords=dynamic_prompt,
        vad_filter=True, # Importante para audios largos
        vad_parameters=dict(min_silence_duration_ms=500, min_speech_duration_ms=500, speech_pad_ms=500)
    )
    
    transcription = ""
    for segment in segments:
        text = segment.text.strip()
        print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {text}")
        transcription += f"**[{segment.start:.2f}s -> {segment.end:.2f}s]** {text}\n\n"
        
    end_time = time.time()
    print(f"\nTranscripción completada en {end_time - start_time:.2f} segundos.")
    
    # Save the output to an artifact folder
    artifact_path = r"C:\Users\carlo\.gemini\antigravity\brain\934258e8-23a2-44ed-acee-abcffb5059d4\transcripcion_clase.md"
    
    md_content = f"# Transcripción de Clase de Prueba\n\n"
    md_content += f"> Audio: {audio_file} (5 Minutos)\n"
    md_content += f"> Modelo: Faster-Whisper 'medium' (CUDA) con Hotwords y VAD Paddings\n"
    md_content += f"> Tiempo de procesamiento: {end_time - start_time:.2f} segundos.\n\n"
    md_content += transcription
    
    with open(artifact_path, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    print(f"Transcripción guardada en {artifact_path}")

if __name__ == "__main__":
    main()

import time
import requests
import json
import argparse

def test_llm(endpoint, model, prompt):
    print(f"Probando servidor LLM en: {endpoint}")
    print(f"Modelo objetivo: {model}\n")
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Sos un asistente preciso. Responde de forma breve y directa usando solo la información provista."},
            {"role": "user", "content": prompt}
        ],
        "stream": True,
        "temperature": 0.1
    }
    
    start_time = time.time()
    first_token_time = None
    token_count = 0
    full_response = ""
    
    print("Enviando prompt...")
    try:
        with requests.post(endpoint, json=payload, headers=headers, stream=True) as response:
            if response.status_code != 200:
                print(f"[*] Error en la conexión: {response.status_code} - {response.text}")
                return
                
            print("Esperando primer token...")
            for line in response.iter_lines():
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
                                    if first_token_time is None:
                                        first_token_time = time.time()
                                        ttft = first_token_time - start_time
                                        print(f"[*] ¡Primer token recibido! (TTFT: {ttft:.3f} segundos)")
                                        print("\n--- Respuesta del Modelo ---")
                                    
                                    print(content, end="", flush=True)
                                    full_response += content
                                    token_count += 1
                        except json.JSONDecodeError:
                            pass
                            
    except requests.exceptions.ConnectionError:
        print("[*] Error de conexión: El servidor no está corriendo o el endpoint es incorrecto.")
        print("[*][*] Si usas Ollama, asegúrate de que esté abierto. Si usas llama-server, verifica el puerto.")
        return
        
    end_time = time.time()
    
    if first_token_time:
        total_time = end_time - start_time
        gen_time = end_time - first_token_time
        tps = token_count / gen_time if gen_time > 0 else 0
        
        print("\n\n--- Resultados de Rendimiento (Fase 2) ---")
        print(f"[*][*] Time to First Token (TTFT): {first_token_time - start_time:.3f} s")
        print(f"[*][*] Tiempo total de respuesta: {total_time:.3f} s")
        print(f"[*][*] Velocidad de generación: {tps:.2f} tokens/s")
        print(f"Tokens totales aproximados: {token_count}")
        print("\n[*][*] IMPORTANTE: Revisa el Administrador de Tareas (Pestaña Rendimiento -> GPU dedicada).")
        print("[*][*] Asegúrate de tener al menos 1.5 - 2 GB de VRAM Libre para Faster-Whisper en la Fase 3.")
    else:
        print("[*] No se recibieron tokens válidos.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test LLM Server Latency")
    parser.add_argument("--endpoint", default="http://localhost:8080/v1/chat/completions", help="URL del endpoint OpenAI compatible (llama-server=8080, Ollama=11434)")
    parser.add_argument("--model", default="qwen2.5-coder", help="Nombre del modelo en el servidor")
    
    args = parser.parse_args()
    
    # Prompt simulando un caso real con RAG
    test_prompt = """Contexto recuperado:

Chunk 1:
"Seguridad en bases de datos"
Es el conjunto de políticas, procedimientos y controles que permiten proteger los datos frente a accesos no autorizados, corrupción o pérdida. Para garantizarla, se aplican diversos mecanismos como la autenticación de usuarios, la gestión de permisos y roles, el cifrado de datos y el registro de auditoría, además de implementar estrategias para prevenir ataques como inyecciones SQL, accesos indebidos y corrupción de datos. Estos controles no solo previenen filtraciones que podrían destruir la reputación corporativa o violar normativas estrictas como GDPR o HIPAA, sino que también aseguran la estabilidad y confidencialidad inherentes a las operaciones empresariales diarias.

Chunk 2:
"Índices en un SGBD"
Son estructuras de datos auxiliares creadas sobre una o más columnas que permiten acelerar el acceso a los datos de una tabla. Funcionan de manera similar a los índices de los libros, facilitando la localización rápida de registros sin necesidad de realizar un recorrido completo de la tabla (lo que optimiza el tiempo de lectura). Sin embargo, implican un costo adicional de espacio y de rendimiento en las operaciones de escritura (INSERT, UPDATE, DELETE), ya que deben mantenerse actualizados constantemente cada vez que la tabla subyacente sufre una modificación. En sistemas con una altísima tasa de escrituras, un exceso de índices puede convertirse en un cuello de botella crítico.

Chunk 3:
"Sistemas de gestión de bases de datos impulsados por IA (Bases de datos autónomas)"
También conocidos por sus siglas en inglés como SDDP (Self-Driving Database Platforms), son plataformas que aprovechan la inteligencia artificial y los algoritmos de aprendizaje automático para automatizar la optimización, el procesamiento de consultas, el ajuste del rendimiento y las tareas de mantenimiento rutinarias de las bases de datos. Su propósito es reducir la carga administrativa de los administradores de bases de datos (DBAs), permitiendo que el sistema perciba, tome decisiones y realice optimizaciones de forma independiente, tales como la gestión de recursos físicos, el ciclo de vida de las instancias, la seguridad y el escalado automático. 

Pregunta del usuario: Durante la reunión mencionaron algo de los índices y su impacto. Según nuestra base de conocimiento, ¿qué problemas traen los índices si tenemos demasiadas operaciones de escritura y por qué?
"""
    
    test_llm(args.endpoint, args.model, test_prompt)

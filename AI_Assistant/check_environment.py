import sys
import platform
import time

try:
    import torch
except ImportError:
    torch = None

try:
    import sounddevice as sd
except ImportError:
    sd = None

def check_cuda():
    print("--- Verificación de GPU y CUDA ---")
    if torch is None:
        print("[*] PyTorch no está instalado. Ejecuta: pip install torch --index-url https://download.pytorch.org/whl/cu121")
        return False
    
    if torch.cuda.is_available():
        print(f"[*] CUDA disponible: SÍ")
        print(f"[*][*] Versión de CUDA (PyTorch): {torch.version.cuda}")
        print(f"[*][*] Dispositivos CUDA detectados: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            print(f"   - Dispositivo {i}: {torch.cuda.get_device_name(i)}")
            
        try:
            free_mem, total_mem = torch.cuda.mem_get_info()
            print(f"   - VRAM Total: {total_mem / (1024**3):.2f} GB")
            print(f"   - VRAM Libre: {free_mem / (1024**3):.2f} GB")
        except Exception as e:
            print("   - No se pudo leer la VRAM exacta.")
        return True
    else:
        print("[*] CUDA disponible: NO")
        print("[*][*] Advertencia: Todo correrá en CPU, afectando severamente la latencia (no se cumplirá el objetivo de 1-3s).")
        return False

def check_audio_devices():
    print("\n--- Verificación de Dispositivos de Audio ---")
    if sd is None:
        print("[*] La librería 'sounddevice' no está instalada. Ejecuta: pip install sounddevice")
        return
    
    print("[*] Dispositivos detectados (Buscando soporte WASAPI):")
    devices = sd.query_devices()
    wasapi_count = 0
    
    for i, dev in enumerate(devices):
        try:
            hostapi = sd.query_hostapis(dev['hostapi'])
            api_name = hostapi['name']
            
            # Mostrar solo WASAPI para no inundar la consola
            if "WASAPI" in api_name:
                wasapi_count += 1
                in_ch = dev['max_input_channels']
                out_ch = dev['max_output_channels']
                print(f"  [{i}] {dev['name']}")
                print(f"      Canales (Entrada/Salida): {in_ch}/{out_ch}")
        except Exception:
            pass
            
    if wasapi_count == 0:
        print("[*][*] No se detectaron dispositivos WASAPI. En Windows es necesario para el loopback.")
    else:
        print("\nNota: Para el loopback (Fase 3), usaremos la API WASAPI capturando la salida de tus auriculares/altavoces.")

def main():
    print(f"=== Diagnóstico del Entorno (Fase 0) ===")
    print(f"Sistema Operativo: {platform.system()} {platform.release()}")
    print(f"Versión de Python: {sys.version.split()[0]}\n")
    
    check_cuda()
    check_audio_devices()
    
    print("\n[*] Fase 0 completada. Si todo está en verde, puedes avanzar a ejecutar test_llm_server.py (Fase 2).")

if __name__ == "__main__":
    main()

import os
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

def parse_master_md(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Separar por "## " que es el formato de conceptos
    chunks = content.split("## ")
    documents = []
    
    for chunk in chunks[1:]:
        lines = chunk.strip().split("\n")
        title = lines[0].strip()
        body = " ".join([line.strip() for line in lines[1:] if line.strip()])
        if title and body:
            documents.append({"title": title, "content": f'"{title}"\n{body}'})
            
    return documents

def main():
    # La ruta al master.md según la estructura del proyecto
    master_path = r"..\Todo BDD\master.md"
    print(f"Leyendo y parseando: {master_path}")
    
    if not os.path.exists(master_path):
        print(f"Error: No se encontró el archivo en {master_path}")
        return
        
    documents = parse_master_md(master_path)
    print(f"Se encontraron {len(documents)} conceptos.")
    
    print("Cargando modelo de embeddings (paraphrase-multilingual-MiniLM-L12-v2)...")
    # Este modelo es ligero y corre perfectamente en CPU o GPU
    model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    
    texts = [doc["content"] for doc in documents]
    
    print("Generando embeddings (esto puede tardar unos segundos)...")
    embeddings = model.encode(texts, show_progress_bar=True)
    embeddings = np.array(embeddings).astype("float32")
    
    print("Creando índice FAISS...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    os.makedirs("index_data", exist_ok=True)
    
    faiss.write_index(index, "index_data/faiss_index.bin")
    with open("index_data/documents.pkl", "wb") as f:
        pickle.dump(documents, f)
        
    print("[*] ¡Índice creado exitosamente en la carpeta 'index_data'!")
    print("Fase 1 completada.")

if __name__ == "__main__":
    main()

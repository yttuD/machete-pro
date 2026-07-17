import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

def main():
    print("Cargando índice FAISS y documentos...")
    index = faiss.read_index("index_data/faiss_index.bin")
    with open("index_data/documents.pkl", "rb") as f:
        documents = pickle.load(f)
        
    print("Cargando modelo de embeddings...")
    model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    
    while True:
        query = input("\nIngresa una consulta (o 'salir'): ")
        if query.lower() == 'salir':
            break
            
        q_emb = model.encode([query]).astype("float32")
        D, I = index.search(q_emb, k=2)
        
        print("\n--- Resultados Principales ---")
        for i in range(len(I[0])):
            idx = I[0][i]
            dist = D[0][i]
            print(f"[{dist:.3f}] {documents[idx]['title']}")

if __name__ == "__main__":
    main()

import os
import chromadb
from sentence_transformers import SentenceTransformer


# ==========================================
# CONFIGURATION
# ==========================================

DOCUMENTS_FOLDER = "documents"
CHROMA_FOLDER = "chroma_db"

COLLECTION_NAME = "knowledge_base"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"


# ==========================================
# LOAD EMBEDDING MODEL
# ==========================================

print("Loading embedding model...")

embedding_model = SentenceTransformer(EMBEDDING_MODEL)

print("Embedding model loaded.")


# ==========================================
# CONNECT TO CHROMADB
# ==========================================

client = chromadb.PersistentClient(
    path=CHROMA_FOLDER
)


# Delete existing collection if it exists
try:
    client.delete_collection(COLLECTION_NAME)
except Exception:
    pass


collection = client.create_collection(
    name=COLLECTION_NAME
)


# ==========================================
# CHUNKING FUNCTION
# ==========================================

def create_chunks(text, chunk_size=500, overlap=100):

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end]

        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


# ==========================================
# LOAD DOCUMENTS
# ==========================================

documents = []
metadatas = []
ids = []


print("\nReading documents...")


for filename in os.listdir(DOCUMENTS_FOLDER):

    file_path = os.path.join(
        DOCUMENTS_FOLDER,
        filename
    )

    if not filename.endswith(".txt"):
        continue

    print("Processing:", filename)

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        text = file.read()


    # Create chunks
    chunks = create_chunks(text)


    for i, chunk in enumerate(chunks):

        documents.append(chunk)

        metadatas.append({
            "source": filename,
            "chunk": i
        })

        ids.append(
            f"{filename}_{i}"
        )


# ==========================================
# CREATE EMBEDDINGS
# ==========================================

print("\nCreating embeddings...")

embeddings = embedding_model.encode(
    documents
).tolist()


# ==========================================
# STORE IN CHROMADB
# ==========================================

print("Storing data in ChromaDB...")


collection.add(

    documents=documents,

    embeddings=embeddings,

    metadatas=metadatas,

    ids=ids
)


# ==========================================
# RESULT
# ==========================================

print("\n===================================")
print("INDEXING COMPLETE")
print("===================================")

print(
    "Documents/chunks stored:",
    len(documents)
)

print(
    "Database:",
    CHROMA_FOLDER
)
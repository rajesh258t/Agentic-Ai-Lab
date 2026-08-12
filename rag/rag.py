import chromadb
import ollama

from sentence_transformers import SentenceTransformer


# ==========================================
# CONFIGURATION
# ==========================================

CHROMA_FOLDER = "chroma_db"

COLLECTION_NAME = "knowledge_base"

OLLAMA_MODEL = "qwen3:8b"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

TOP_K = 3


# ==========================================
# LOAD EMBEDDING MODEL
# ==========================================

print("Loading embedding model...")

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)

print("Embedding model loaded.")


# ==========================================
# CONNECT TO CHROMADB
# ==========================================

client = chromadb.PersistentClient(
    path=CHROMA_FOLDER
)

collection = client.get_collection(
    name=COLLECTION_NAME
)


# ==========================================
# RETRIEVAL FUNCTION
# ==========================================

def retrieve_documents(question):

    # Convert question into embedding
    question_embedding = embedding_model.encode(
        question
    ).tolist()


    # Search ChromaDB
    results = collection.query(

        query_embeddings=[
            question_embedding
        ],

        n_results=TOP_K
    )


    documents = results["documents"][0]

    metadatas = results["metadatas"][0]

    distances = results["distances"][0]


    return documents, metadatas, distances


# ==========================================
# GENERATION FUNCTION
# ==========================================

def generate_answer(question, documents):

    # Combine retrieved documents
    context = "\n\n".join(documents)


    prompt = f"""
You are a helpful question-answering assistant.

Answer the user's question using ONLY the information
provided in the context.

If the answer cannot be found in the context,
say:

"I don't know based on the provided documents."

Do not invent information.

CONTEXT:
----------------------------

{context}

----------------------------

QUESTION:

{question}

ANSWER:
"""


    # Send prompt to Qwen3
    response = ollama.chat(

        model=OLLAMA_MODEL,

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )


    return response["message"]["content"]


# ==========================================
# COMPLETE RAG PIPELINE
# ==========================================

def rag(question):

    print("\nSearching knowledge base...")


    # STEP 1: RETRIEVAL
    documents, metadatas, distances = retrieve_documents(
        question
    )


    # Show retrieved documents
    print("\nRetrieved documents:")
    print("--------------------------------")


    for i, (doc, metadata, distance) in enumerate(
        zip(documents, metadatas, distances)
    ):

        print(
            f"\n[{i + 1}] "
            f"Source: {metadata['source']} "
            f"Chunk: {metadata['chunk']}"
        )

        print(doc)

        print(
            f"Distance: {distance:.4f}"
        )


    # STEP 2: GENERATION
    answer = generate_answer(
        question,
        documents
    )


    return answer


# ==========================================
# CHAT LOOP
# ==========================================

print("\n===================================")
print("LOCAL RAG QUESTION ANSWERING SYSTEM")
print("===================================")

print("Model:", OLLAMA_MODEL)

print("Type 'exit' to quit.")


while True:

    question = input("\nYou: ")


    if question.lower() == "exit":
        print("Goodbye!")
        break


    if not question.strip():
        continue


    answer = rag(question)


    print("\nQwen3:")
    print("--------------------------------")

    print(answer)
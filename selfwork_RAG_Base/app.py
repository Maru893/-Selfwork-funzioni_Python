import os
from dotenv import load_dotenv
from openai import OpenAI
import chromadb
from chromadb.utils import embedding_functions


load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")

if not openai_key:
    raise ValueError("Manca OPENAI_API_KEY nel file .env")


client = OpenAI(api_key=openai_key)

documents_dir = "resumes"

documents = []
metadatas = []
ids = []

current_id = 0

for filename in os.listdir(documents_dir):
    if filename.endswith(".txt"):
        file_path = os.path.join(documents_dir, filename)

        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read().replace("\n", ".")
            chunks = content.split("### ")

            info = chunks[1] if len(chunks) > 1 else chunks[0]

            for chunk in chunks:
                if chunk.strip() != "":
                    documents.append(chunk)
                    metadatas.append({
                        "source": filename,
                        "info": info
                    })
                    ids.append(str(current_id))
                    current_id += 1


print(f"Documenti caricati: {len(documents)}")

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=openai_key,
    model_name="text-embedding-3-small"
)

chroma_client = chromadb.Client()

collection = chroma_client.get_or_create_collection(
    name="CVs",
    embedding_function=openai_ef
)

collection.add(
    documents=documents,
    metadatas=metadatas,
    ids=ids
)

user_question = "mi serve qualcuno per gestire un progetto digitale"

results = collection.query(
    query_texts=[user_question],
    n_results=1
)

documento_trovato = results["documents"][0][0]
metadata_trovato = results["metadatas"][0][0]

context = f"""
CONTESTO:
Nome file: {metadata_trovato["source"]}

Paragrafo più significativo:
{documento_trovato}

Ricorda sempre di menzionare il candidato all'inizio
e i dati personali alla fine per il contatto.

Informazioni candidato:
{metadata_trovato["info"]}
"""

prompt = f"""
Dato il seguente contesto:

{context}

Rispondi alla domanda dell'utente:

{user_question}

Spiega che nel file individuato c'è il profilo più adatto.
Argomenta la scelta utilizzando il contenuto del testo individuato nel contesto.
"""

completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
       {
            "role": "developer",
            "content": "Sei un assistente HR, specializzato nella ricerca di profili professionali. Rispondi sempre in italiano naturale, senza usare parole inglesi se esiste un equivalente italiano."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
)

print("\nRisposta finale:\n")
print(completion.choices[0].message.content)
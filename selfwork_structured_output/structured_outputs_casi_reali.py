
import json
import os
from enum import Enum
from typing import Optional

import openai
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field


# SETUP


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")



# ESERCIZIO 1
# Analisi di un ticket di assistenza clienti


class TicketCategory(str, Enum):
    ordine = "ordine"
    pagamento = "pagamento"
    spedizione = "spedizione"
    reso = "reso"
    problema_tecnico = "problema_tecnico"
    altro = "altro"


class TicketPriority(str, Enum):
    bassa = "bassa"
    media = "media"
    alta = "alta"
    urgente = "urgente"


class CustomerSentiment(str, Enum):
    positivo = "positivo"
    neutro = "neutro"
    negativo = "negativo"
    arrabbiato = "arrabbiato"


class SupportTicketAnalysis(BaseModel):
    summary: str = Field(description="Riassunto breve del problema del cliente")
    category: TicketCategory = Field(description="Categoria principale del ticket")
    priority: TicketPriority = Field(description="Priorità del ticket")
    sentiment: CustomerSentiment = Field(description="Stato emotivo del cliente")
    order_id: Optional[str] = Field(description="Codice ordine, se presente")
    customer_request: str = Field(description="Cosa chiede concretamente il cliente")
    needs_human_operator: bool = Field(description="True se serve un operatore umano")
    suggested_reply: str = Field(description="Risposta consigliata da inviare al cliente")
    next_steps: list[str] = Field(description="Azioni operative da fare")


def analyze_support_ticket(ticket_text: str) -> SupportTicketAnalysis:
    completion = client.chat.completions.parse(
        model=MODEL,
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": (
                    "Sei un assistente per un team customer care. "
                    "Devi leggere un messaggio cliente e trasformarlo in un oggetto strutturato. "
                    "Non inventare dati non presenti. Se il codice ordine manca, usa null."
                ),
            },
            {
                "role": "user",
                "content": ticket_text,
            },
        ],
        response_format=SupportTicketAnalysis,
    )

    message = completion.choices[0].message

    if message.refusal:
        raise ValueError(f"Il modello ha rifiutato la richiesta: {message.refusal}")

    return message.parsed


def run_example_1() -> None:
    print("\n" + "=" * 80)
    print("ESEMPIO 1 - Analisi ticket assistenza clienti")
    print("=" * 80)

    ticket = """
    Buongiorno, ho ordinato delle cuffie wireless il 10 giugno.
    Il codice ordine è ORD-88421.
    Il pacco risulta consegnato, ma dentro mancava il caricatore.
    Ho già scritto due volte ma non ho ricevuto risposta.
    Vorrei ricevere il caricatore oppure un rimborso parziale.
    """

    result = analyze_support_ticket(ticket)

    print("\nOggetto Pydantic:")
    print(result)

    print("\nAccesso ai campi con il punto:")
    print("Categoria:", result.category.value)
    print("Priorità:", result.priority.value)
    print("Codice ordine:", result.order_id)
    print("Serve operatore umano:", result.needs_human_operator)

    print("\nRisposta consigliata:")
    print(result.suggested_reply)

    print("\nAzioni operative:")
    for step in result.next_steps:
        print("-", step)



# ESERCIZIO 2
# Estrazione parametri per ricerca immobiliare utilizzando come output strutturato too call


class ContractType(str, Enum):
    affitto = "affitto"
    vendita = "vendita"
    qualsiasi = "qualsiasi"


class RealEstateSearchParameters(BaseModel):
    city: str = Field(description="Città in cui cercare casa")
    neighborhoods: list[str] = Field(description="Quartieri o zone preferite")
    max_budget_eur: int = Field(description="Budget massimo in euro")
    min_rooms: int = Field(description="Numero minimo di locali")
    furnished: Optional[bool] = Field(description="True se cerca casa arredata, False se non arredata, null se non specificato")
    contract_type: ContractType = Field(description="Tipo di contratto")
    must_have: list[str] = Field(description="Caratteristiche indispensabili")
    nice_to_have: list[str] = Field(description="Caratteristiche gradite ma non indispensabili")
    move_in_month: Optional[str] = Field(description="Mese di ingresso, se presente")


def fake_real_estate_database_search(params: RealEstateSearchParameters) -> list[dict]:
    """
    Questa funzione simula una ricerca in un database immobiliare.

    In un progetto vero, qui potresti interrogare:
    - un database SQL
    - un file CSV
    - una API immobiliare
    - un motore di ricerca interno
    """

    fake_database = [
        {
            "title": "Trilocale arredato vicino metro Dante",
            "city": "Torino",
            "neighborhood": "San Salvario",
            "price": 1100,
            "rooms": 3,
            "furnished": True,
            "features": ["metro", "balcone", "ascensore"],
        },
        {
            "title": "Bilocale moderno in Crocetta",
            "city": "Torino",
            "neighborhood": "Crocetta",
            "price": 950,
            "rooms": 2,
            "furnished": True,
            "features": ["tram", "portineria"],
        },
        {
            "title": "Trilocale non arredato zona Vanchiglia",
            "city": "Torino",
            "neighborhood": "Vanchiglia",
            "price": 1050,
            "rooms": 3,
            "furnished": False,
            "features": ["università", "balcone"],
        },
    ]

    results = []

    for house in fake_database:
        if house["city"].lower() != params.city.lower():
            continue

        if house["price"] > params.max_budget_eur:
            continue

        if house["rooms"] < params.min_rooms:
            continue

        if params.furnished is not None and house["furnished"] != params.furnished:
            continue

        if params.neighborhoods:
            requested_zones = [zone.lower() for zone in params.neighborhoods]
            if house["neighborhood"].lower() not in requested_zones:
                continue

        results.append(house)

    return results


def extract_real_estate_search_parameters(user_request: str) -> RealEstateSearchParameters:
    completion = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "Sei un assistente immobiliare. "
                    "Il tuo compito è trasformare la richiesta dell'utente "
                    "in parametri strutturati per cercare case in un database."
                ),
            },
            {
                "role": "user",
                "content": user_request,
            },
        ],
        tools=[
            openai.pydantic_function_tool(
                RealEstateSearchParameters,
                name="search_real_estate",
                description="Cerca case in base ai parametri dell'utente",
            )
        ],
        tool_choice={
            "type": "function",
            "function": {"name": "search_real_estate"},
        },
    )

    tool_call = completion.choices[0].message.tool_calls[0]
    arguments = json.loads(tool_call.function.arguments)

    return RealEstateSearchParameters(**arguments)


def run_example_2() -> None:
    print("\n" + "=" * 80)
    print("ESEMPIO 2 - Parametri strutturati per ricerca immobiliare")
    print("=" * 80)

    user_request = """
    Cerco un trilocale in affitto a Torino, massimo 1200 euro al mese.
    Preferirei San Salvario o Crocetta, vicino alla metro o ai mezzi.
    Mi serve arredato e vorrei entrare da settembre.
    Se ha il balcone è meglio.
    """

    params = extract_real_estate_search_parameters(user_request)

    print("\nParametri estratti dal modello:")
    print(params.model_dump_json(indent=2))

    results = fake_real_estate_database_search(params)

    print("\nRisultati trovati nel database finto:")
    if not results:
        print("Nessun risultato trovato.")
        return

    for item in results:
        print("-" * 40)
        print("Titolo:", item["title"])
        print("Città:", item["city"])
        print("Zona:", item["neighborhood"])
        print("Prezzo:", item["price"], "euro")
        print("Locali:", item["rooms"])
        print("Arredato:", "sì" if item["furnished"] else "no")
        print("Caratteristiche:", ", ".join(item["features"]))



# MAIN


if __name__ == "__main__":
    run_example_1()
    run_example_2()

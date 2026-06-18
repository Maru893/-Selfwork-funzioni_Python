"""
Esercizio: 2 esempi reali di Structured Outputs

differenza tra:
  1. output strutturato come risposta del modello
  2. output strutturato come tool call per interrogare un sistema/backend

### APPUNTI:

Nel primo esempio il modello legge un messaggio cliente e restituisce un oggetto con campi precisi:

Quindi non ricevi una risposta generica, ma dati già pronti da usare in un’app.

Nel secondo esempio il modello non deve “rispondere bene”, ma deve preparare i parametri per una funzione:

Poi il codice usa quei parametri per cercare dentro un database finto.

Questa è la differenza importante:

Structured output semplice:
il modello produce un oggetto finale.

Tool call:
il modello produce argomenti strutturati per chiamare una funzione.

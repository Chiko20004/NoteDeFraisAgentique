# TicketMain

Application agentique de gestion des notes de frais. Tu prends en photo un ticket, l'app extrait les infos et les envoie dans un Google Sheet.

Réalisé par Cherif Kamel — HETIC DIA2

---

## Stack

- Python, FastAPI
- Llama 4 Scout via Groq SDK
- Google Sheets API + Google Drive API
- HTML, HTMX, JS Vanilla

---

## Installation

```bash
git clone https://github.com/Chiko20004/NoteDeFraisAgentique.git
cd NoteDeFraisAgentique
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## Configuration

Copie `.env.example` en `.env` et remplis :
GROQ_API_KEY=""
GOOGLE_SHEET_ID=""
GOOGLE_SERVICE_ACCOUNT_JSON=""
GOOGLE_DRIVE_FOLDER_ID=""

---

## Google Cloud

1. Créer un projet Google Cloud
2. Activer Sheets API et Drive API
3. Créer un compte de service et télécharger la clé JSON
4. Partager le Sheet et un dossier Drive avec l'email du compte de service

---

## Lancer

```bash
python -m uvicorn main:app --reload
```

Ouvre http://127.0.0.1:8000

---

## Exemple JSON retourné

```json
{
  "type_document": "supermarche",
  "fournisseur": "Walmart",
  "date": "08/01/12",
  "montant_ttc": 63.82,
  "tva": 5.2,
  "devise": "USD",
  "description": "3 articles",
  "confiance": "haute"
}
```
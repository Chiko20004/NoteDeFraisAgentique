import os
import base64
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from backend import ExpenseAgent
from sheets import GoogleSheetsClient
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

agent = ExpenseAgent()
sheets_client = GoogleSheetsClient()

ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"]
MAX_SIZE = 10 * 1024 * 1024


@app.get("/", response_class=FileResponse)
async def index():
    return FileResponse("static/index.html")


@app.post("/api/analyze", response_class=HTMLResponse)
async def analyze(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        return HTMLResponse(
            content='<div class="error">Format non supporte. Utilise JPG, PNG ou WEBP.</div>',
            status_code=400
        )

    image_bytes = await file.read()

    if len(image_bytes) > MAX_SIZE:
        return HTMLResponse(
            content='<div class="error">Image trop lourde. Maximum 10MB.</div>',
            status_code=400
        )

    try:
        data = agent.extract_from_bytes(image_bytes, file.content_type)
    except Exception as e:
        return HTMLResponse(
            content=f'<div class="error">Erreur analyse : {str(e)}</div>',
            status_code=500
        )

    image_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    image_data = f"data:{file.content_type};base64,{image_b64}"

    html = f"""
    <form hx-post="/api/submit" hx-target="#confirmation-container" hx-encoding="application/x-www-form-urlencoded">
        <div class="form-group">
            <label>Type de document</label>
            <select name="type_document">
                <option value="restaurant" {"selected" if data.get("type_document") == "restaurant" else ""}>Restaurant</option>
                <option value="supermarche" {"selected" if data.get("type_document") == "supermarche" else ""}>Supermarche</option>
                <option value="pharmacie" {"selected" if data.get("type_document") == "pharmacie" else ""}>Pharmacie</option>
                <option value="autre" {"selected" if data.get("type_document") == "autre" else ""}>Autre</option>
            </select>
        </div>
        <div class="form-group">
            <label>Fournisseur</label>
            <input type="text" name="fournisseur" value="{data.get('fournisseur') or ''}">
        </div>
        <div class="form-group">
            <label>Date</label>
            <input type="text" name="date" value="{data.get('date') or ''}">
        </div>
        <div class="form-group">
            <label>Montant TTC</label>
            <input type="number" step="0.01" name="montant_ttc" value="{data.get('montant_ttc') or ''}">
        </div>
        <div class="form-group">
            <label>TVA</label>
            <input type="number" step="0.01" name="tva" value="{data.get('tva') or ''}">
        </div>
        <div class="form-group">
            <label>Devise</label>
            <input type="text" name="devise" value="{data.get('devise') or 'EUR'}">
        </div>
        <div class="form-group">
            <label>Description</label>
            <input type="text" name="description" value="{data.get('description') or ''}">
        </div>
        <div class="form-group">
            <label>Confiance</label>
            <select name="confiance">
                <option value="haute" {"selected" if data.get("confiance") == "haute" else ""}>Haute</option>
                <option value="moyen" {"selected" if data.get("confiance") == "moyen" else ""}>Moyen</option>
                <option value="basse" {"selected" if data.get("confiance") == "basse" else ""}>Basse</option>
            </select>
        </div>
        <input type="hidden" name="image_data" value="{image_data}">
        <button type="submit" class="btn-submit">Envoyer vers Google Sheets</button>
    </form>
    """
    return HTMLResponse(content=html)


@app.post("/api/submit", response_class=HTMLResponse)
async def submit(
    type_document: str = Form(None),
    fournisseur: str = Form(None),
    date: str = Form(None),
    montant_ttc: str = Form(None),
    tva: str = Form(None),
    devise: str = Form(None),
    description: str = Form(None),
    confiance: str = Form(None),
    image_data: str = Form(None)
):
    data = {
        "type_document": type_document,
        "fournisseur": fournisseur,
        "date": date,
        "montant_ttc": float(montant_ttc) if montant_ttc else None,
        "tva": float(tva) if tva else None,
        "devise": devise,
        "description": description,
        "confiance": confiance
    }

    image_url = None

    try:
        if image_data:
            header, encoded = image_data.split(",", 1)
            media_type = header.split(":")[1].split(";")[0]
            image_bytes = base64.b64decode(encoded)
            filename = f"ticket_{fournisseur}_{date}.jpg".replace("/", "-")
            image_url = sheets_client.upload_image_to_drive(image_bytes, filename, media_type)
    except Exception as e:
        print(f"Erreur upload image : {e}")

    try:
        sheets_client.append_expense(data, image_url)
    except Exception as e:
        return HTMLResponse(
            content=f'<div class="error">Erreur Google Sheets : {str(e)}</div>',
            status_code=500
        )

    return HTMLResponse(content="""
        <div class="success">
            Note de frais envoyee avec succes.
            <button onclick="window.location.reload()" class="btn-reset">Nouvelle note</button>
        </div>
    """)
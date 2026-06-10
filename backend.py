import os
import base64
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class ExpenseAgent:
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct"
        
        # On récupère les chemins absolus pour éviter les problèmes de répertoire
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        with open(os.path.join(base_dir, "context.txt"), "r", encoding="utf-8") as f:
            self.system_prompt = f.read()
            
        with open(os.path.join(base_dir, "prompt.txt"), "r", encoding="utf-8") as f:
            self.user_prompt = f.read()
    
    def extract_from_bytes(self, image_bytes: bytes, media_type: str) -> dict:
        # On encode l'image en base64 pour l'envoyer au modèle
        image_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
        
        response = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{image_b64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": self.user_prompt
                        }
                    ]
                }
            ]
        )
        
        # On parse le JSON retourné par le modèle
        result = json.loads(response.choices[0].message.content)
        
        # On s'assure que tous les champs sont présents même si le modèle les a oubliés
        expected_fields = [
            "type_document", "fournisseur", "date",
            "montant_ttc", "tva", "devise",
            "description", "confiance"
        ]
        
        for field in expected_fields:
            if field not in result:
                result[field] = None
                
        return result


# Test rapide en ligne de commande
if __name__ == "__main__":
    agent = ExpenseAgent()
    
    # Remplace par le chemin d'un vrai ticket pour tester
    test_image_path = "test_ticket.jpg"
    
    if not os.path.exists(test_image_path):
        print("Mets une image test_ticket.jpg dans le dossier pour tester")
    else:
        with open(test_image_path, "rb") as f:
            image_bytes = f.read()
            
        result = agent.extract_from_bytes(image_bytes, "image/jpeg")
        print(json.dumps(result, indent=2, ensure_ascii=False))
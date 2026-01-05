from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
import json
import os

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI()

# Gemini client (NEW correct way)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Load products
with open("products.json") as f:
    products = json.load(f)

cart = []

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(req: ChatRequest):
    user_msg = req.message.lower()

    if "show" in user_msg or "products" in user_msg:
        return {"reply": products}

    if "add" in user_msg:
        for p in products:
            if p["name"].lower() in user_msg:
                cart.append(p)
                return {"reply": f"{p['name']} added to cart."}

    if "checkout" in user_msg:
        total = sum(p["price"] for p in cart)
        order = {
            "items": cart,
            "total": total,
            "status": "confirmed"
        }
        cart.clear()
        return {"reply": order}

    # Gemini AI response
    response = client.models.generate_content(
        model="gemini-pro",
        contents=req.message
    )

    return {"reply": response.text}

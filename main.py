from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import SessionLocal, engine
from models import Product, Base
import google.generativeai as genai
from dotenv import load_dotenv
import os

# --------------------------------------------------
# LOAD ENV VARIABLES
# --------------------------------------------------
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# --------------------------------------------------
# APP SETUP
# --------------------------------------------------
app = FastAPI()

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create DB tables
Base.metadata.create_all(bind=engine)

# --------------------------------------------------
# IN-MEMORY CART
# --------------------------------------------------
cart = []

# --------------------------------------------------
# REQUEST SCHEMA
# --------------------------------------------------
class ChatRequest(BaseModel):
    message: str

# --------------------------------------------------
# SEED PRODUCTS ON STARTUP
# --------------------------------------------------
@app.on_event("startup")
def seed_products():
    db = SessionLocal()
    try:
        if db.query(Product).count() == 0:
            products = [
                Product(
                    name="Backpack",
                    price=2500,
                    description="Durable travel backpack",
                    stock=10,
                ),
                Product(
                    name="Headphones",
                    price=1500,
                    description="Wireless headphones",
                    stock=15,
                ),
                Product(
                    name="Smart Watch",
                    price=3500,
                    description="Fitness smart watch",
                    stock=8,
                ),
            ]
            db.add_all(products)
            db.commit()
    finally:
        db.close()

# --------------------------------------------------
# CHAT ENDPOINT
# --------------------------------------------------
@app.post("/chat")
def chat(request: ChatRequest):
    user_message = request.message.lower()
    db = SessionLocal()

    try:
        # -------------------------
        # SHOW PRODUCTS
        # -------------------------
        if "show" in user_message or "products" in user_message:
            products = db.query(Product).all()
            if not products:
                return {"reply": "No products available."}

            response = "🛍️ Available products:\n"
            for p in products:
                response += f"- {p.name} : ₹{p.price}\n"
            return {"reply": response}

        # -------------------------
        # ADD TO CART
        # -------------------------
        if "add" in user_message:
            products = db.query(Product).all()
            for p in products:
                if p.name.lower() in user_message:
                    cart.append(p)
                    return {"reply": f"✅ {p.name} added to cart. Anything else?"}
            return {"reply": "❌ Product not found."}

        # -------------------------
        # CHECKOUT
        # -------------------------
        if "checkout" in user_message:
            if not cart:
                return {"reply": "🛒 Your cart is empty."}

            total = sum(p.price for p in cart)
            cart.clear()
            return {
                "reply": f"🎉 Order confirmed!\nTotal amount: ₹{total}"
            }

        # -------------------------
        # GEMINI AI RESPONSE
        # -------------------------
        ai_response = model.generate_content(user_message)
        return {"reply": ai_response.text}

    except Exception as e:
        return {"reply": f"⚠️ Error: {str(e)}"}

    finally:
        db.close()

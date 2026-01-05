import express from "express";
import cors from "cors";
import products from "./products.json" assert { type: "json" };
import { addToCart, getCart, checkout } from "./cart.js";
import { getAIResponse } from "./gemini.js";

const app = express();
app.use(cors());
app.use(express.json());

app.post("/chat", async (req, res) => {
  const userMessage = req.body.message.toLowerCase();

  if (userMessage.includes("show")) {
    return res.json({ reply: products });
  }

  if (userMessage.includes("add")) {
    const product = products.find(p =>
      userMessage.includes(p.name.toLowerCase())
    );
    if (product) {
      addToCart(product);
      return res.json({ reply: `${product.name} added to cart.` });
    }
  }

  if (userMessage.includes("checkout")) {
    const order = checkout();
    return res.json({ reply: order });
  }

  // fallback to Gemini
  const aiReply = await getAIResponse(userMessage);
  res.json({ reply: aiReply });
});

app.listen(5000, () => console.log("Server running on port 5000"));

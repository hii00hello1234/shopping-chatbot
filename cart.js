let cart = [];

export function addToCart(product, qty = 1) {
  cart.push({ ...product, quantity: qty });
}

export function getCart() {
  return cart;
}

export function checkout() {
  const total = cart.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  );

  const order = {
    items: cart,
    total,
    status: "confirmed"
  };

  cart = []; 
  return order;
}

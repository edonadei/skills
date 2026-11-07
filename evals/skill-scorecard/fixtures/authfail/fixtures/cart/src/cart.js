import { percentOf } from './money.js';

export const VAT_PERCENT = 20;

export function subtotal(cart) {
  return cart.items.reduce((sum, item) => sum + item.unitCents * item.qty, 0);
}

// Prices are VAT-exclusive; the total the customer pays includes VAT.
export function total(cart) {
  const net = subtotal(cart);
  return net + percentOf(net, VAT_PERCENT);
}

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { subtotal, total } from '../src/cart.js';

const cart = { items: [{ sku: 'MUG', unitCents: 1250, qty: 2 }, { sku: 'TEE', unitCents: 1999, qty: 1 }] };

test('subtotal', () => assert.equal(subtotal(cart), 4499));
test('total includes VAT', () => assert.equal(total(cart), 5399));

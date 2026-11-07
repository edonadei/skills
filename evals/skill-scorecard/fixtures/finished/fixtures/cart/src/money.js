// All money is integer cents. Round half away from zero, like the payment provider.
export function roundCents(value) {
  return Math.sign(value) * Math.round(Math.abs(value));
}

export function percentOf(cents, percent) {
  return roundCents((cents * percent) / 100);
}

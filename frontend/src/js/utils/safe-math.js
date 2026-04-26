// Safe math for BigInt/crypto
window.WOC_SafeMath = {
  add: (a, b) => (BigInt(a) + BigInt(b)).toString(),
  sub: (a, b) => (BigInt(a) - BigInt(b)).toString(),
  mul: (a, b) => (BigInt(a) * BigInt(b)).toString(),
  div: (a, b) => (BigInt(a) / BigInt(b)).toString()
};

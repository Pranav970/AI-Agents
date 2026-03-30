const { randomUUID } = require('crypto');
function generateCode() {
  return randomUUID().slice(0,7);  // e.g. use first 7 chars
}

export const SUPPORTED_BARCODE_FORMATS = ['ean_13', 'ean_8', 'upc_a', 'upc_e']

/**
 * Expands an 8-digit UPC-E barcode into its equivalent 12-digit UPC-A code.
 * Returns the original value if it does not match the 8-digit UPC-E format.
 */
export function expandUpcE(code) {
  if (!/^[01]\d{7}$/.test(code)) return code

  const numberSystem = code[0]
  const d1 = code[1]
  const d2 = code[2]
  const d3 = code[3]
  const d4 = code[4]
  const d5 = code[5]
  const d6 = code[6]
  const checkDigit = code[7]

  let manufacturer
  let product

  if (d6 === '0' || d6 === '1' || d6 === '2') {
    manufacturer = `${d1}${d2}${d6}00`
    product = `00${d3}${d4}${d5}`
  } else if (d6 === '3') {
    manufacturer = `${d1}${d2}${d3}00`
    product = `000${d4}${d5}`
  } else if (d6 === '4') {
    manufacturer = `${d1}${d2}${d3}${d4}0`
    product = `0000${d5}`
  } else {
    manufacturer = `${d1}${d2}${d3}${d4}${d5}`
    product = `0000${d6}`
  }

  return `${numberSystem}${manufacturer}${product}${checkDigit}`
}

/**
 * Validates GS1 Mod-10 check digit for EAN-8 (8), UPC-A (12), and EAN-13 (13).
 */
export function isValidGtinCheckDigit(code) {
  if (!code || !/^\d+$/.test(code)) return false
  if (![8, 12, 13].includes(code.length)) return false

  const digits = code.split('').map(Number)
  const checkDigit = digits.pop()

  let sum = 0
  for (let i = 0; i < digits.length; i++) {
    const weight = (digits.length - i) % 2 === 1 ? 3 : 1
    sum += digits[i] * weight
  }

  const calculated = (10 - (sum % 10)) % 10
  return checkDigit === calculated
}

/**
 * Normalizes a scanned barcode value, expanding UPC-E to 12-digit UPC-A when needed.
 */
export function normalizeScannedBarcode(rawValue, format = '') {
  if (!rawValue) return ''
  const cleaned = String(rawValue).trim().replace(/\s+/g, '')
  if (format === 'upc_e' && cleaned.length === 8) {
    return expandUpcE(cleaned)
  }
  return cleaned
}

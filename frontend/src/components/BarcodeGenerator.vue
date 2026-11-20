<template>
  <div class="barcode-container text-center">
    <svg v-show="value" ref="barcodeRef"></svg>
    <div v-if="!value" class="text-caption text-negative">
      Invalid or missing barcode value.
    </div>
    <div v-else-if="usedFallback" class="text-caption text-warning q-mt-xs">
      Invalid check digit — rendered as CODE128
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import JsBarcode from 'jsbarcode'

const props = defineProps({
  value: {
    type: String,
    default: ''
  },
  format: {
    type: String,
    default: ''
  }
})

const barcodeRef = ref(null)
const usedFallback = ref(false)

const resolveFormat = (code) => {
  if (props.format) return props.format
  if (/^\d{13}$/.test(code)) return 'EAN13'
  if (/^\d{8}$/.test(code)) return 'EAN8'
  if (/^\d{12}$/.test(code)) return 'UPC'
  return 'CODE128'
}

const renderBarcode = (code, format) => {
  JsBarcode(barcodeRef.value, code, {
    format,
    background: '#ffffff',
    lineColor: '#000000',
    width: 2,
    height: 110,
    margin: 18,
    displayValue: true,
    fontSize: 16
  })
}

const generateBarcode = () => {
  nextTick(() => {
    if (!barcodeRef.value) return

    const code = props.value?.trim()
    usedFallback.value = false

    if (!code) {
      barcodeRef.value.innerHTML = ''
      return
    }

    const preferredFormat = resolveFormat(code)

    try {
      renderBarcode(code, preferredFormat)
    } catch {
      // Fallback to CODE128 if the stored code has an invalid EAN/UPC check digit
      if (preferredFormat !== 'CODE128') {
        try {
          renderBarcode(code, 'CODE128')
          usedFallback.value = true
          return
        } catch (fallbackError) {
          console.error('Erro ao gerar barcode:', fallbackError)
        }
      }
      barcodeRef.value.innerHTML = ''
    }
  })
}

onMounted(generateBarcode)

watch([() => props.value, () => props.format], generateBarcode)
</script>

<style scoped>
.barcode-container svg {
  display: block;
  margin: 0 auto;
  max-width: 100%;
  height: auto;
  shape-rendering: crispEdges;
}
</style>
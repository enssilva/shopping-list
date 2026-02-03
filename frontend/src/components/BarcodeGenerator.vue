<template>
  <div class="barcode-container text-center">
    <svg ref="barcodeRef"></svg>
    <div v-if="!value" class="text-caption text-negative">
      Invalid or missing barcode value.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import JsBarcode from 'jsbarcode'

const props = defineProps({
  value: {
    type: String,
    required: true
  },
  format: {
    type: String,
    default: 'EAN13' // Padrão mais comum em Vitória
  }
})

const barcodeRef = ref(null)

const generateBarcode = () => {
  nextTick(() => { // Garante que o elemento existe no DOM
    if (props.value && barcodeRef.value) {
      try {
        JsBarcode(barcodeRef.value, props.value, {
          format: props.value.length === 8 ? 'EAN8' : 'CODE128', // CODE128 é mais flexível para testes
          lineColor: "#000",
          width: 2,
          height: 100,
          displayValue: true
        })
      } catch (e) {
        console.error('Erro ao gerar barcode:', e)
      }
    }
  })
}

// Gera ao montar o componente
onMounted(generateBarcode)

// Atualiza se o valor mudar (ex: navegando entre produtos)
watch(() => props.value, generateBarcode)
</script>

<style scoped>
.barcode-container svg {
  max-width: 100%;
  height: auto;
}
</style>
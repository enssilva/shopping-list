<template>
  <div class="barcode-scanner">
    <div id="reader" style="width: 100%"></div>

    <div class="q-gutter-y-sm q-mt-md">
      <q-btn
        v-if="!isScanning"
        color="primary"
        icon="qr_code_scanner"
        label="Start Scanner"
        @click="startScanner"
        class="full-width"
      />
      <q-btn
        v-else
        color="negative"
        icon="stop"
        label="Stop Scanner"
        @click="stopScanner"
        class="full-width"
      />

      <div class="text-center text-grey-7 q-my-sm">OR</div>

      <q-input
        v-model="manualBarcode"
        label="Manual Barcode Entry"
        outlined
        dense
        mask="#############" 
        unmasked-value
        :rules="[ val => !val || val.length === 8 || val.length === 13 || 'Use 8 or 13 digits' ]"
        lazy-rules
        @keyup.enter="handleManualSearch"
      >
        <template v-slot:append>
          <q-btn 
            round 
            flat 
            icon="search" 
            @click="handleManualSearch" 
            :disable="!isValidLength"
          />
        </template>
      </q-input>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onBeforeUnmount } from 'vue'
import { useQuasar } from 'quasar'
import { Html5QrcodeScanner } from 'html5-qrcode'
import { api } from 'boot/axios'

const emit = defineEmits(['detected'])
const $q = useQuasar()
const isScanning = ref(false)
const manualBarcode = ref('')
let html5QrcodeScanner = null

// Validação de comprimento para padrões EAN-8 e EAN-13
const isValidLength = computed(() => {
  const len = manualBarcode.value.length
  return len === 8 || len === 13
})

// Lógica compartilhada para processar o código de barras
const processBarcode = async (barcode) => {
  try {
    // Busca o produto usando a rota correta de código de barras
    const response = await api.get(`/products/barcode/${barcode}`)
    emit('detected', { 
      exists: true, 
      product: response.data 
    })
    manualBarcode.value = '' // Limpa o campo após sucesso
  } catch {
    // Se o produto não existir (404), emite para criação
    // Removida variável de erro para evitar conflito com ESLint
    emit('detected', { 
      exists: false, 
      barcode: barcode 
    })
  }
}

const onScanSuccess = async (decodedText) => {
  if (isScanning.value) {
    isScanning.value = false
    if (html5QrcodeScanner) {
      await html5QrcodeScanner.clear()
    }
    await processBarcode(decodedText)
  }
}

const handleManualSearch = () => {
  if (isValidLength.value) {
    processBarcode(manualBarcode.value)
  } else {
    // Agora o $q estará definido e o ESLint não reclamará
    $q.notify({
      message: 'Please enter a valid 8 or 13 digit barcode',
      color: 'warning',
      position: 'top',
      icon: 'warning'
    })
  }
}

const onScanFailure = () => {
  // Ignora falhas de frame para não poluir logs
}

const startScanner = () => {
  isScanning.value = true
  html5QrcodeScanner = new Html5QrcodeScanner(
    'reader',
    { fps: 10, qrbox: { width: 250, height: 150 } },
    false
  )
  html5QrcodeScanner.render(onScanSuccess, onScanFailure)
}

const stopScanner = async () => {
  if (html5QrcodeScanner) {
    await html5QrcodeScanner.clear()
    isScanning.value = false
  }
}

onBeforeUnmount(async () => {
  if (isScanning.value && html5QrcodeScanner) {
    await html5QrcodeScanner.clear()
  }
})
</script>

<style scoped>
.barcode-scanner {
  max-width: 500px;
  margin: 0 auto;
}
#reader {
  border: 2px solid #ccc;
  border-radius: 8px;
  overflow: hidden;
  background: #f8f8f8;
}
</style>
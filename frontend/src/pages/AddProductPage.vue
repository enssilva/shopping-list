<template>
  <q-page class="q-pa-md">
    <div class="text-h5 q-mb-md">Add Product</div>

    <q-form ref="myForm" @submit="saveAll" class="q-gutter-md">
      
      <q-select
        v-model="selectedList"
        :options="userLists"
        option-label="name"
        label="Select your Shopping List (Optional)"
        outlined
        clearable
        class="q-mb-md"
      />

      <BarcodeScanner ref="scannerRef" @detected="onProductDetected" />

      <div v-if="scannedBarcode" class="flex justify-center q-mt-sm">
        <q-btn 
          flat 
          color="grey-7" 
          icon="refresh" 
          label="Clear / Rescan" 
          @click="resetPage" 
        />
      </div>

      <q-card v-if="scannedBarcode || productExists" flat bordered>
        <q-card-section class="q-gutter-md">
          
          <div :class="isEanValid ? 'text-positive' : 'text-negative'" class="text-subtitle2">
            Barcode: {{ scannedBarcode }} 
            <q-icon :name="isEanValid ? 'check_circle' : 'warning'" />
            <span v-if="!isEanValid" class="q-ml-xs">(Invalid EAN-13 check digit)</span>
          </div>

          <q-input
            v-model="productForm.name"
            label="Product Name *"
            outlined
            :rules="[
              val => !!val || 'Name is required',
              () => isEanValid || 'Check digit is invalid.'
            ]"
            :disable="productExists"
          />

          <q-select
            v-model="productForm.market_id"
            :options="markets"
            option-value="id"
            option-label="name"
            emit-value
            map-options
            label="Market (Optional)"
            outlined
            clearable
          />

          <q-input
            v-model.number="productForm.price"
            label="Price (Optional)"
            type="number"
            step="0.01"
            outlined
            clearable
          />

          <q-btn
            label="Save Product"
            type="submit" 
            color="primary"
            class="full-width"
            :loading="isSaving"
            :disable="!isEanValid"
          />
        </q-card-section>
      </q-card>
    </q-form>
  </q-page>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { api } from 'src/boot/axios'
import { useAuthStore } from 'src/stores/auth'
import { useQuasar } from 'quasar'
import BarcodeScanner from 'src/components/BarcodeScanner.vue'
import { useRoute } from 'vue-router'

const $q = useQuasar()
const authStore = useAuthStore()

// State
const userLists = ref([])
const selectedList = ref(null)
const loadingLists = ref(false)
const scannedBarcode = ref('')
const productExists = ref(false)
const isSaving = ref(false)
const markets = ref([])

const productForm = ref({
  name: '',
  market_id: null,
  price: 0,
  product_id: null
})

const route = useRoute()

// Validação EAN-13
const isEanValid = computed(() => {
  const code = scannedBarcode.value
  if (!code || code.length !== 13) return false
  
  const digits = code.split('').map(Number)
  const lastDigit = digits.pop()
  const sum = digits.reduce((acc, digit, idx) => acc + (idx % 2 === 0 ? digit : digit * 3), 0)
  const calculatedCheckDigit = (10 - (sum % 10)) % 10
  return lastDigit === calculatedCheckDigit
})

const scannerRef = ref(null)

const myForm = ref(null)

async function loadInitialData() {
  loadingLists.value = true
  try {
    const [listsRes, marketsRes] = await Promise.all([
      api.get(`/lists/${authStore.userId}`),
      api.get('/markets/')
    ])
    userLists.value = listsRes.data
    markets.value = marketsRes.data
    const listIdFromUrl = route.params.listId
    if (listIdFromUrl) {
      selectedList.value = userLists.value.find(l => l.id === parseInt(listIdFromUrl))
    }
  } catch {
    $q.notify({ color: 'negative', message: 'Error loading lists or markets' })
  } finally {
    loadingLists.value = false
  }
}

function onProductDetected(data) {
  scannedBarcode.value = data.barcode || data.product.barcode
  productExists.value = data.exists

  if (data.exists) {
    productForm.value.name = data.product.name
    productForm.value.product_id = data.product.id
  } else {
    productForm.value.name = ''
    productForm.value.product_id = null
  }
}

async function saveAll() {
  const success = await myForm.value.validate()
  if (!success) return

  isSaving.value = true
  try {
    let productId = productForm.value.product_id

    // 1. Criação/Identificação do Produto
    if (!productExists.value) {
      const prodRes = await api.post('/products/', {
        name: productForm.value.name,
        barcode: scannedBarcode.value
      })
      productId = prodRes.data.id
    }

    // 2. Preço (Opcional)
    if (productForm.value.market_id && productForm.value.price > 0) {
      await api.post('/prices/', {
        product_id: productId,
        market_id: productForm.value.market_id,
        price: productForm.value.price,
        user_id: authStore.userId
      })
    }

    // 3. Lista (Opcional) - Protegido para não disparar erro no Catch principal
    if (selectedList.value?.id) {
      try {
        await api.post('/lists/items', {
          shopping_list_id: selectedList.value.id,
          product_id: productId,
          quantity: 1
        })
      } catch (listErr) {
        console.warn("Product saved, but failed to add to list", listErr)
      }
    }

    $q.notify({ color: 'positive', message: 'Product saved successfully!' })
    
    // IMPORTANTE: Limpeza total
    resetPage()

  } catch (error) {
    console.error(error)
    $q.notify({ color: 'negative', message: 'Failed to save product' })
  } finally {
    isSaving.value = false
  }
}

function resetPage() {
  // 1. Limpa a variável que controla a exibição do card
  scannedBarcode.value = ''
  
  // 2. Reseta o formulário
  productForm.value = {
    name: '',
    price: 0,
    market_id: null,
    product_id: null
  }
  
  productExists.value = false
  
  // 3. Se o seu componente BarcodeScanner tiver um método de reset, 
  if (scannerRef.value) {
    scannerRef.value.reset()
  }

  // 4. Limpa validações do formulário
  if (myForm.value) {
    myForm.value.resetValidation()
  }
}

  

onMounted(loadInitialData)
</script>
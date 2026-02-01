<template>
  <q-page class="q-pa-md">
    <div class="row items-center justify-between q-mb-md">
      <div class="text-h5">Product Catalog</div>
      <q-btn color="primary" icon="add" label="New Scan" to="/add-product" />
    </div>

    <q-input
      v-model="searchQuery"
      placeholder="Search by name or barcode..."
      outlined
      dense
      class="q-mb-md"
      @update:model-value="onSearch"
      clearable
    >
      <template v-slot:append>
        <q-icon name="search" />
      </template>
    </q-input>

    <div v-if="loading" class="flex flex-center q-pa-lg">
      <q-spinner-dots color="primary" size="40px" />
    </div>

    <div v-else-if="products.length > 0" class="row q-col-gutter-md">
      <div v-for="product in products" :key="product.id" class="col-12 col-sm-6 col-md-4">
        <q-card flat bordered>
          <q-card-section class="row items-center no-wrap">
            <q-avatar icon="inventory_2" color="blue-1" text-color="primary" />
            <div class="q-ml-md">
              <div class="text-h6 text-weight-bold">{{ product.name }}</div>
              <div class="text-caption text-grey-8">Barcode: {{ product.barcode }}</div>
            </div>
          </q-card-section>

          <q-separator />

          <q-card-actions align="right">
            <q-btn flat color="primary" icon="history" label="Prices" @click="viewPriceHistory(product)" />
            <q-btn flat color="negative" icon="delete" @click="confirmDelete(product)" />
          </q-card-actions>
        </q-card>
      </div>
    </div>

    <q-card v-else flat bordered class="text-center q-pa-lg">
      <q-card-section class="text-grey-7">
        No products found in your database.
      </q-card-section>
    </q-card>
  </q-page>
  <q-dialog v-model="priceDialog.show">
    <q-card style="min-width: 350px">
      <q-toolbar class="q-pr-sm">
        <q-toolbar-title>
          <span class="text-weight-bold">Price History:</span> 
          <div class="text-subtitle2 text-grey-8">{{ priceDialog.productName }}</div>
        </q-toolbar-title>

        <q-btn flat round dense icon="close" v-close-popup color="grey-7" />
      </q-toolbar>

      <q-separator />

      <q-card-section v-if="loadingPrices" class="text-center q-pa-lg">
        <q-spinner-dots color="primary" size="40px" />
      </q-card-section>

      <q-card-section v-else class="q-pt-none">
        <q-list separator v-if="priceHistory.length > 0">
          <q-item v-for="price in priceHistory" :key="price.id" class="q-px-none">
            <q-item-section>
              <q-item-label class="text-h6 text-primary text-weight-bolder">
                R$ {{ price.price.toFixed(2) }}
              </q-item-label>
              <q-item-label caption class="text-grey-9">
                <q-icon name="store" size="xs" class="q-mr-xs" />
                {{ price.market?.name || 'Unknown Market' }}
              </q-item-label>
            </q-item-section>
            
            <q-item-section side top>
              <q-item-label caption class="q-mt-sm">
                <q-icon name="event" size="xs" class="q-mr-xs" />
                {{ new Date(price.updated_at).toLocaleDateString('pt-BR') }}
              </q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
        
        <div v-else class="text-center q-pa-md text-grey-7">
          No price records found.
        </div>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from 'src/boot/axios'
import { useQuasar } from 'quasar'

const $q = useQuasar()
const products = ref([])
const searchQuery = ref('')
const loading = ref(true)
const priceDialog = ref({ show: false, productName: '' })
const priceHistory = ref([])
const loadingPrices = ref(false)
let timeout = null

async function fetchProducts() {
  loading.value = true
  try {
    // 1. Se a busca estiver vazia, carrega todos os produtos
    if (!searchQuery.value) {
      const response = await api.get('/products/')
      products.value = response.data
      return
    }

    // 2. Verifica se a busca contém apenas números (Regex)
    const isOnlyNumbers = /^\d+$/.test(searchQuery.value)

    if (isOnlyNumbers) {
      try {
        // Busca específica por código de barras
        const response = await api.get(`/products/barcode/${searchQuery.value}`)
        // Como o endpoint retorna um objeto único, colocamos dentro de uma lista
        products.value = [response.data]
      } catch {
        // Se der 404 (não encontrado), limpamos a lista sem erro
        products.value = []
      }
    } else {
      // 3. Busca por nome se houver letras ou mistura
      const response = await api.get(`/products/search?q=${searchQuery.value}`)
      products.value = response.data
    }
  } catch {
    // Tratamento genérico de erro (sem a variável para o ESLint)
    $q.notify({ color: 'negative', message: 'Error fetching products', icon: 'erro' })
  } finally {
    loading.value = false
  }
}

function onSearch() {
  clearTimeout(timeout)
  timeout = setTimeout(() => {
    fetchProducts()
  }, 300)
}

async function confirmDelete(product) {
$q.dialog({
    title: 'Confirm Deletion',
    message: `Are you sure you want to delete "${product.name}"? This action cannot be undone.`,
    persistent: true,
    ok: {
      label: 'Delete',
      color: 'negative',
      flat: true
    },
    cancel: {
      label: 'Cancel',
      color: 'primary',
      flat: true
    }
  }).onOk(async () => {
    try {
      await api.delete(`/products/${product.id}`)
      products.value = products.value.filter(p => p.id !== product.id)
      $q.notify({
        color: 'positive',
        message: 'Product removed successfully',
        icon: 'delete'
      })
    } catch {
      $q.notify({
        color: 'negative',
        message: 'Failed to delete product. Check if it has linked prices.',
        icon: 'error'
      })
    }
  })
}

async function viewPriceHistory(product) {
  priceDialog.value.show = true
  priceDialog.value.productName = product.name
  loadingPrices.value = true
  
  try {
    const response = await api.get(`/prices/history/${product.id}`)
    priceHistory.value = response.data
  } catch {
    $q.notify({ color: 'negative', message: 'Error loading prices' })
    priceDialog.value.show = false
  } finally {
    loadingPrices.value = false
  }
}

onMounted(fetchProducts)
</script>
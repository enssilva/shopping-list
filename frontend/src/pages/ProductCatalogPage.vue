<template>
  <q-page padding>
    <div class="row q-col-gutter-md">
      <div class="col-12">
        <q-input
          v-model="searchQuery"
          label="Search products (name or barcode)"
          outlined
          clearable
          @keyup.enter="fetchProducts"
        >
          <template v-slot:append>
            <q-btn round flat icon="search" @click="fetchProducts" />
          </template>
        </q-input>
      </div>

      <div v-if="loading" class="col-12 flex justify-center q-pa-lg">
        <q-spinner color="primary" size="3em" />
      </div>

      <div v-else-if="products.length === 0" class="col-12 text-center q-pa-lg">
        <p class="text-grey-7">No products found.</p>
        <q-btn color="primary" label="Add New Product" to="/add-product" />
      </div>

      <div v-for="product in products" :key="product.id" class="col-12 col-sm-6 col-md-4">
        <q-card class="product-card">
          <q-card-section>
            <div class="text-h6">{{ product.name }}</div>
            <div class="text-subtitle2 text-grey-7">Barcode: {{ product.barcode }}</div>
          </q-card-section>

          <q-separator />

          <q-card-actions align="right">
            <q-btn flat color="primary" icon="edit" @click="openEditDialog(product)" />
            <q-btn flat color="primary" label="View Prices" @click="showPrices(product)" />
            <q-btn flat color="negative" icon="delete" @click="confirmDelete(product)" />
          </q-card-actions>
        </q-card>
      </div>
    </div>

    <q-dialog v-model="priceDialog.show">
      <q-card style="width: 400px; max-width: 90vw;">
        <q-toolbar class="bg-primary text-white">
          <q-toolbar-title>{{ selectedProduct?.name }}</q-toolbar-title>
          <q-btn flat round dense icon="close" v-close-popup />
        </q-toolbar>

        <q-card-section class="flex justify-center q-pa-md bg-grey-1">
          <div class="text-center">
            <div class="text-caption q-mb-xs">Digital Barcode</div>
            <BarcodeGenerator :value="selectedProduct?.barcode" />
          </div>
        </q-card-section>

        <q-card-section>
          <div class="text-subtitle1 q-mb-sm">Price History</div>
          <q-list bordered separator v-if="priceHistory.length > 0">
            <q-item v-for="price in priceHistory" :key="price.id">
              <q-item-section>
                <q-item-label>{{ price.market?.name || 'Unknown Market' }}</q-item-label>
                <q-item-label caption>{{ formatDate(price.date) }}</q-item-label>
              </q-item-section>
              <q-item-section side>
                <q-item-label class="text-weight-bold text-primary">
                  R$ {{ price.price.toFixed(2) }}
                </q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
          <div v-else class="text-center q-pa-md text-grey-7">
            No prices registered for this product.
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
    <q-dialog v-model="editDialog.show">
      <q-card style="min-width: 350px">
        <q-card-section>
          <div class="text-h6">Edit Product</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input 
            v-model="editDialog.name" 
            label="Product Name" 
            outlined 
            dense 
            autofocus
            @keyup.enter="saveProductEdit"
          />
        </q-card-section>

        <q-card-actions align="right" class="text-primary">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn flat label="Save" @click="saveProductEdit" :loading="editDialog.loading" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { api } from 'boot/axios'
import BarcodeGenerator from 'components/BarcodeGenerator.vue'

const $q = useQuasar()
const searchQuery = ref('')
const products = ref([])
const loading = ref(false)
const selectedProduct = ref(null)
const priceHistory = ref([])
const priceDialog = ref({ show: false })

const editDialog = ref({
  show: false,
  loading: false,
  id: null,
  name: ''
})

function confirmDelete(product) {
  $q.dialog({
    title: 'Confirm Deletion',
    message: `Delete ${product.name}? This will remove all associated prices.`,
    cancel: true,
    persistent: true
  }).onOk(async () => {
    try {
      await api.delete(`/products/${product.id}`)
      $q.notify({ color: 'positive', message: 'Product deleted' })
      fetchProducts()
    } catch {
      $q.notify({ color: 'negative', message: 'Delete failed' })
    }
  })
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('pt-BR')
}

function openEditDialog(product) {
  editDialog.value = {
    show: true,
    loading: false,
    id: product.id,
    name: product.name
  }
}

async function fetchProducts() {
  loading.value = true
  try {
    const isOnlyNumbers = /^\d+$/.test(searchQuery.value)
    
    if (searchQuery.value && isOnlyNumbers) {
      try {
        // Busca na rota específica de barcode do seu backend
        const response = await api.get(`/products/barcode/${searchQuery.value}`)
        products.value = [response.data]
      } catch {
        products.value = []
      }
    } else {
      const endpoint = searchQuery.value ? `/products/search?q=${searchQuery.value}` : '/products/'
      const response = await api.get(endpoint)
      products.value = response.data
    }
  } catch {
    $q.notify({ color: 'negative', message: 'Error loading products', icon: 'error' })
  } finally {
    loading.value = false
  }
}

async function showPrices(product) {
  selectedProduct.value = product
  try {
    // Busca o histórico com o market_id vinculado corretamente
    const response = await api.get(`/prices/product/${product.id}`)
    priceHistory.value = response.data
    priceDialog.value.show = true
  } catch {
    $q.notify({ color: 'negative', message: 'Error loading price history' })
  }
}

async function saveProductEdit() {
  if (!editDialog.value.name) return
  
  editDialog.value.loading = true
  try {
    await api.put(`/products/${editDialog.value.id}`, {
      name: editDialog.value.name
    })
    $q.notify({ color: 'positive', message: 'Product updated successfully' })
    editDialog.value.show = false
    fetchProducts() // Recarrega a lista
  } catch {
    $q.notify({ color: 'negative', message: 'Error updating product' })
  } finally {
    editDialog.value.loading = false
  }
}

onMounted(fetchProducts)
</script>

<style scoped>
.product-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
</style>
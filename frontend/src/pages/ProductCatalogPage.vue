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

    <q-page padding>
      <q-page-sticky position="bottom-right" :offset="[18, 18]">
        <q-btn 
          fab 
          icon="add" 
          color="primary" 
          to="/add-product"
        >
          <q-tooltip>Add New Product</q-tooltip>
        </q-btn>
      </q-page-sticky>
    </q-page>

    <q-dialog v-model="priceDialog.show">
      <q-card style="width: 450px; max-width: 90vw;">
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
          <div class="text-subtitle2 q-mb-sm">Add New Price</div>
          <div class="row q-col-gutter-sm">
            <div class="col-12 col-sm-6">
              <q-select
                v-model="newPrice.market_id"
                :options="markets"
                option-value="id"
                option-label="name"
                emit-value
                map-options
                label="Market"
                outlined
                dense
              />
            </div>

            <div class="col-6 col-sm-6">
              <q-input
                v-model.number="newPrice.value"
                label="Price (R$)"
                type="number"
                step="0.01"
                outlined
                dense
              />
            </div>

            <div class="col-6 col-sm-12">
              <q-input 
                v-model="newPrice.date" 
                label="Date" 
                outlined 
                dense
                mask="####-##-##"
                placeholder="Today"
              >
                <template v-slot:append>
                  <q-icon name="event" class="cursor-pointer">
                    <q-popup-proxy ref="dateProxy" cover transition-show="scale" transition-hide="scale">
                      <q-date
                        v-model="newPrice.date"
                        mask="YYYY-MM-DD"
                        @update:model-value="() => $refs.dateProxy.hide()"
                      >
                        <div class="row items-center justify-end">
                          <q-btn v-close-popup label="Close" color="primary" flat />
                        </div>
                      </q-date>
                    </q-popup-proxy>
                  </q-icon>

                  <q-separator vertical inset class="q-mx-sm" />
                  
                  <q-btn 
                    flat 
                    round 
                    color="primary" 
                    icon="add" 
                    @click="addNewPrice" 
                    :loading="newPrice.loading"
                    dense
                  >
                    <q-tooltip>Add Price Entry</q-tooltip>
                  </q-btn>
                </template>
              </q-input>
            </div>
          </div>
        </q-card-section>

        <q-separator />

        <q-card-section style="max-height: 40vh" class="scroll">
          <div class="text-subtitle1 q-mb-sm">Price History</div>
          <q-list bordered separator v-if="priceHistory.length > 0">
            <q-item v-for="price in priceHistory" :key="price.id">
              <q-item-section>
                <q-item-label>{{ price.market?.name || 'Unknown Market' }}</q-item-label>
                <q-item-label
                  caption
                  :class="formatDate(price.updated_at || price.date) === 'Hoje' ? 'text-weight-bold text-positive' : ''"
                >
                  {{ formatDate(price.updated_at || price.date) }}
                </q-item-label>
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
import { useAuthStore } from 'src/stores/auth' // Importação necessária
import BarcodeGenerator from 'components/BarcodeGenerator.vue'

const $q = useQuasar()
const authStore = useAuthStore() // Inicialização necessária

const searchQuery = ref('')
const products = ref([])
const loading = ref(false)
const selectedProduct = ref(null)
const priceHistory = ref([])
const priceDialog = ref({ show: false })

const markets = ref([]) // Lista de mercados para o select
const newPrice = ref({
  market_id: null,
  value: 0,
  date: null,
  loading: false
})

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

// function formatDate(dateString) {
//   if (!dateString) return 'N/A'
//   return new Date(dateString).toLocaleDateString('pt-BR')
// }
function formatDate(dateString) {
  if (!dateString) return 'N/A'
  
  const date = new Date(dateString)
  const today = new Date()
  
  // Normaliza as datas para comparar apenas o dia, mês e ano
  const isSameDay = (d1, d2) => 
    d1.getDate() === d2.getDate() &&
    d1.getMonth() === d2.getMonth() &&
    d1.getFullYear() === d2.getFullYear()

  // Ontem
  const yesterday = new Date()
  yesterday.setDate(today.getDate() - 1)

  if (isSameDay(date, today)) {
    return 'Hoje'
  } else if (isSameDay(date, yesterday)) {
    return 'Ontem'
  } else {
    // Retorna a data formatada para o padrão brasileiro
    return date.toLocaleDateString('pt-BR')
  }
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

async function loadMarkets() {
  try {
    const res = await api.get('/markets/')
    markets.value = res.data
  } catch {
    $q.notify({ color: 'negative', message: 'Error loading markets' })
  }
}

async function showPrices(product) {
  selectedProduct.value = product
  try {
    const response = await api.get(`/prices/product/${product.id}`)
    priceHistory.value = response.data
    priceDialog.value.show = true
  } catch {
    $q.notify({ color: 'negative', message: 'Error loading price history' })
  }
}

async function addNewPrice() {
  if (newPrice.value.market_id === null || newPrice.value.value <= 0) {
    $q.notify({ color: 'warning', message: 'Select a market and a valid price' })
    return
  }

  newPrice.value.loading = true
  try {
    // Montamos o payload para o backend
    // Uso correto do authStore para vincular o preço ao usuário logado
    const payload = {
      product_id: Number(selectedProduct.value.id),
      market_id: Number(newPrice.value.market_id), // Forçamos para Number
      price: Number(newPrice.value.value),
      user_id: Number(authStore.userId)
    }    
    // Só adicionamos updated_at se o usuário selecionou uma data
    if (newPrice.value.date && newPrice.value.date.trim() !== '') {
      payload.updated_at = newPrice.value.date
    }
    await api.post('/prices/', payload)
    
    $q.notify({ color: 'positive', message: 'Price added!' })
    
    // Reseta o formulário
    newPrice.value.value = 0
    newPrice.value.date = null
    // newPrice.value.market_id = null
    showPrices(selectedProduct.value)
  } catch (error) {
    console.error("Erro completo:", error.response?.data)
    $q.notify({ color: 'negative', message: 'Failed to record price' })
  } finally {
    newPrice.value.loading = false
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
    fetchProducts()
  } catch {
    $q.notify({ color: 'negative', message: 'Error updating product' })
  } finally {
    editDialog.value.loading = false
  }
}

onMounted(() => {
  fetchProducts()
  loadMarkets() // Carrega os mercados disponíveis para Vitória
})
</script>

<style scoped>
.product-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
</style>
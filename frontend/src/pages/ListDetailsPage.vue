<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-gutter-sm q-mb-md">
      <q-btn icon="arrow_back" flat round dense to="/shopping-list" />
      <div v-if="listData" class="text-h5">{{ listData.name }}</div>
      <q-space />
      <q-btn-dropdown
        flat
        round
        color="primary"
        icon="content_paste"
      >
        <q-list>
          <q-item clickable v-close-popup @click="exportToMarkdown('full')">
            <q-item-section avatar>
              <q-icon name="table_chart" color="primary" />
            </q-item-section>
            <q-item-section>
              <q-item-label>Lista Completa (Tabela)</q-item-label>
              <q-item-label caption>Com preços e quantidades</q-item-label>
            </q-item-section>
          </q-item>

          <q-item clickable v-close-popup @click="exportToMarkdown('simple')">
            <q-item-section avatar>
              <q-icon name="checklist" color="primary" />
            </q-item-section>
            <q-item-section>
              <q-item-label>Lista Simples (Checklist)</q-item-label>
              <q-item-label caption>Apenas nomes e marcações</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
      </q-btn-dropdown>
    </div>

    <div v-if="loading" class="flex flex-center q-pa-lg">
      <q-spinner-dots color="primary" size="40px" />
    </div>

    <div v-else-if="listData">
      <p v-if="listData.description" class="text-subtitle2 text-grey-8 q-mb-lg">
        {{ listData.description }}
      </p>

      <q-list bordered separator class="rounded-borders">
        <q-item-label header>Products in this list</q-item-label>

        <q-item v-for="item in listData.items" :key="item.id" class="q-py-md">
          <q-item-section avatar>
            <q-checkbox 
              v-model="item.is_checked" 
              color="primary" 
              @click.stop
              @update:model-value="toggleItemStatus(item)"
            />
          </q-item-section>

          <q-item-section clickable @click="showPriceComparison(item)" class="cursor-pointer">
            <q-item-label 
              class="text-weight-bold text-h6"
              :class="{ 'text-strike text-grey-6': item.is_checked }"
            >
              {{ item.product?.name || 'Unknown Product' }}
            </q-item-label>
            <q-item-label caption>
              Barcode: {{ item.product?.barcode }}
            </q-item-label>
          </q-item-section>

          <q-item-section side @click.stop>
            <div class="row items-center q-gutter-x-sm">
              <q-btn 
                flat round dense icon="remove" size="sm" color="primary"
                :disable="item.quantity <= 1"
                @click="updateQuantity(item, item.quantity - 1)" 
              />
              <div class="text-subtitle1 text-weight-bold" style="min-width: 20px; text-align: center;">
                {{ item.quantity }}
              </div>
              <q-btn 
                flat round dense icon="add" size="sm" color="primary"
                @click="updateQuantity(item, item.quantity + 1)" 
              />
            </div>
          </q-item-section>
        
          <q-item-section side @click.stop>
            <q-btn flat round color="negative" icon="delete" @click="removeItem(item.id)" />
          </q-item-section>
        </q-item>

        <q-item v-if="listData.items.length === 0" class="text-center q-pa-lg">
          <q-item-section class="text-grey">
            This list has no products yet. 
            Go to "Add Product" to start scanning.
          </q-item-section>
        </q-item>
      </q-list>

    </div>
    <q-page-sticky position="bottom-right" :offset="[18, 18]">
      <q-btn fab icon="add" color="primary" @click="showAddDialog = true">
        <q-tooltip>Add existing product</q-tooltip>
      </q-btn>
    </q-page-sticky>

    <q-dialog v-model="showAddDialog" persistent>
      <q-card style="min-width: 350px">
        <q-card-section>
          <div class="text-h6">Add Existing Product</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-select
            v-model="selectedProduct"
            use-input
            input-debounce="300"
            label="Search by name or barcode"
            :options="productOptions"
            @filter="filterProducts"
            option-label="name"
            outlined
            autofocus
          >
            <template v-slot:option="scope">
              <q-item v-bind="scope.itemProps">
                <q-item-section>
                  <q-item-label>{{ scope.opt.name }}</q-item-label>
                  <q-item-label caption>{{ scope.opt.barcode }}</q-item-label>
                </q-item-section>
              </q-item>
            </template>
            <template v-slot:no-option>
              <q-item>
                <q-item-section class="text-grey">No results found</q-item-section>
              </q-item>
            </template>
          </q-select>
        </q-card-section>

        <q-card-actions align="right" class="text-primary">
          <q-btn flat label="Cancel" v-close-popup @click="resetSelection" />
          <q-btn 
            flat 
            label="Add to List" 
            @click="addProductToList" 
            :disable="!selectedProduct" 
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
    <q-dialog v-model="priceDialog.show">
      <q-card style="min-width: 350px">
        <q-card-section class="row items-center">
          <div class="text-h6">{{ priceDialog.productName }}</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-list separator>
            <q-item v-for="price in priceDialog.prices" :key="price.id">
              <q-item-section avatar>
                <q-icon name="storefront" color="grey-7" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ price.market.name }}</q-item-label>
                <q-item-label caption>Atualizado em: {{ formatDate(price.updated_at) }}</q-item-label>
              </q-item-section>
              <q-item-section side>
                <q-badge color="green-7" label class="text-subtitle2">
                  {{ formatCurrency(price.price) }}
                </q-badge>
              </q-item-section>
            </q-item>
            
            <q-item v-if="priceDialog.prices.length === 0">
              <q-item-section class="text-grey text-center">
                Nenhum outro preço cadastrado para este produto.
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from 'src/boot/axios'
import { useQuasar, exportFile } from 'quasar'

const $q = useQuasar()
const route = useRoute()
const loading = ref(true)
const listData = ref(null)
const showAddDialog = ref(false)
const selectedProduct = ref(null)
const productOptions = ref([])
const priceDialog = ref({
  show: false,
  productName: '',
  prices: []
})

/**
 * Resets the selection state
 */
function resetSelection() {
  selectedProduct.value = null
  productOptions.value = []
}

/**
 * Fetches the specific list details using the ID from the URL
 */
async function fetchListDetails() {
  loading.value = true
  try {
    const listId = route.params.id
    // This endpoint must return the list object with nested items
    const response = await api.get(`/lists/details/${listId}`)
    listData.value = response.data
  } catch {
    $q.notify({
      color: 'negative',
      message: 'Failed to load list details',
      icon: 'error'
    })
  } finally {
    loading.value = false
  }
}

/**
 * Removes an item from the current list
 * @param {number} itemId
 */
async function removeItem(itemId) {
  try {
    await api.delete(`/lists/items/${itemId}`)
    listData.value.items = listData.value.items.filter(i => i.id !== itemId)
    $q.notify({ color: 'positive', message: 'Item removed', icon: 'delete', position: 'bottom' })
  } catch {
    $q.notify({ color: 'negative', message: 'Error removing item', icon: 'error' })
  }
}

/**
 * Updates the quantity of an item and persists to backend
 * @param {Object} item - The shopping list item object
 * @param {number} newQty - The target quantity
 */
async function updateQuantity(item, newQty) {
  if (newQty < 1) return

  try {
    // Calling the PATCH endpoint created above
    await api.patch(`/lists/items/${item.id}?quantity=${newQty}`)
    
    // Update local state for immediate feedback
    item.quantity = newQty
    
    $q.notify({
      color: 'positive',
      message: 'Quantity updated',
      timeout: 500,
      position: 'bottom'
    })
  } catch {
    $q.notify({
      color: 'negative',
      message: 'Failed to update quantity',
      icon: 'error'
    })
  }
}

/**
 * Searches for products in the database as the user types
 */
async function filterProducts(val, update) {
  if (val.length < 2) {
    update(() => { productOptions.value = [] })
    return
  }

  try {
    // Replace with your actual product search endpoint
    const response = await api.get(`/products/search?q=${encodeURIComponent(val)}`)
    update(() => {
      productOptions.value = response.data
    })
  } catch {
    update(() => { productOptions.value = [] })
  }
}

/**
 * Persists the selected product to the current shopping list
 */
async function addProductToList() {
  if (!selectedProduct.value) return

  try {
    const listId = route.params.id
    await api.post('/lists/items', {
      shopping_list_id: parseInt(listId),
      product_id: selectedProduct.value.id,
      quantity: 1
    })

    $q.notify({ color: 'positive', message: 'Product added to list' })
    showAddDialog.value = false
    resetSelection()
    fetchListDetails() // Refresh the list to show the new item
  } catch {
    $q.notify({ color: 'negative', message: 'Failed to add product' })
  }
}

// Função para alternar o status do item
async function toggleItemStatus(item) {
  try {
    // O backend espera o corpo JSON com is_checked
    await api.patch(`/lists/items/${item.id}`, {
      is_checked: item.is_checked
    })
    
    $q.notify({
      color: 'positive',
      message: item.is_checked ? 'Item marcado' : 'Item desmarcado',
      timeout: 500
    })
  } catch {
    item.is_checked = !item.is_checked
    $q.notify({ color: 'negative', message: 'Erro ao atualizar status', icon: 'cloud_off' })
  }
}

function showPriceComparison(item) {
  // O backend já traz os preços se você usar o joinedload no endpoint de detalhes
  priceDialog.value.productName = item.product.name
  priceDialog.value.prices = item.product.prices || []
  priceDialog.value.show = true
}

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('pt-BR')
}

function formatCurrency(value) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)
}

function exportToMarkdown(type = 'full') {
  if (!listData.value) return

  let md = `# ${listData.value.name}\n\n`
  
  if (type === 'full') {
    // Formato 1: Tabela Completa
    md += `| Status | Produto | Qtd | Preços |\n`
    md += `| :---: | :--- | :---: | :--- |\n`
    
    listData.value.items.forEach(item => {
      const status = item.is_checked ? '[x]' : '[ ]'
      const prices = item.product?.prices?.length 
        ? item.product.prices.map(p => `${p.market.name}: ${formatCurrency(p.price)}`).join('<br>')
        : '---'
      
      md += `| ${status} | ${item.product?.name} | ${item.quantity} | ${prices} |\n`
    })
  } else {
    // Formato 2: Checklist Simples
    listData.value.items.forEach(item => {
      const status = item.is_checked ? '- [x]' : '- [ ]'
      md += `${status} ${item.product?.name}\n`
    })
  }

  // Copia para a área de transferência
  navigator.clipboard.writeText(md).then(() => {
    $q.notify({
      color: 'positive',
      message: `Markdown (${type === 'full' ? 'Completo' : 'Simples'}) copiado!`,
      icon: 'check',
      timeout: 1000
    })
  }).catch(() => {
    // Fallback: Se falhar (em navegadores antigos), tenta baixar o arquivo
    const status = exportFile(`${listData.value.name}.md`, md)
    if (status !== true) $q.notify({ color: 'negative', message: 'Erro ao exportar' })
  })
}

onMounted(fetchListDetails)
</script>

<style scoped>
/* Classe para riscar o texto de itens comprados */
.text-strike {
  text-decoration: line-through;
}
</style>
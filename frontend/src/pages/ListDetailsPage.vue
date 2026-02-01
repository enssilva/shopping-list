<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-gutter-sm q-mb-md">
      <q-btn icon="arrow_back" flat round dense to="/shopping-list" />
      <div v-if="listData" class="text-h5">{{ listData.name }}</div>
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
          <q-item-section>
            <q-item-label class="text-weight-bold text-h6">
              {{ item.product?.name || 'Unknown Product' }}
            </q-item-label>
            <q-item-label caption>
              Barcode: {{ item.product?.barcode }}
            </q-item-label>
          </q-item-section>
        
          <q-item-section side>
            <div class="row items-center q-gutter-x-sm">
              <q-btn 
                flat round dense 
                icon="remove" 
                size="sm" 
                color="primary"
                :disable="item.quantity <= 1"
                @click="updateQuantity(item, item.quantity - 1)" 
              />
              <div class="text-subtitle1 text-weight-bold" style="min-width: 20px; text-align: center;">
                {{ item.quantity }}
              </div>
              <q-btn 
                flat round dense 
                icon="add" 
                size="sm" 
                color="primary"
                @click="updateQuantity(item, item.quantity + 1)" 
              />
            </div>
          </q-item-section>
        
          <q-item-section side>
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

      <div class="row justify-end q-mt-md">
        <q-chip outline color="primary" text-color="primary" icon="calculate" size="lg">
          Estimated Total: R$ {{ totalSum.toFixed(2) }}
        </q-chip>
      </div>
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
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from 'src/boot/axios'
import { useQuasar } from 'quasar'

const $q = useQuasar()
const route = useRoute()
const loading = ref(true)
const listData = ref(null)
const showAddDialog = ref(false)
const selectedProduct = ref(null)
const productOptions = ref([])

/**
 * Sums the price of all items in the current list
 */
const totalSum = computed(() => {
  if (!listData.value || !listData.value.items) return 0
  return listData.value.items.reduce((sum, item) => sum + (item.price || 0), 0)
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
    const response = await api.get(`/products/search?q=${val}`)
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

onMounted(fetchListDetails)
</script>
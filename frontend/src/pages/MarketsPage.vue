<template>
  <q-page class="q-pa-md">
    <div class="row items-center justify-between q-mb-md">
      <div class="text-h5 text-weight-bold">Markets Management</div>
      <q-btn color="primary" icon="add" label="Add Market" @click="openMarketDialog()" />
    </div>

    <div v-if="loading" class="flex flex-center q-pa-lg">
      <q-spinner-dots color="primary" size="40px" />
    </div>

    <div v-else-if="markets.length > 0" class="row q-col-gutter-md">
      <div v-for="market in markets" :key="market.id" class="col-12 col-sm-6 col-md-4">
        <q-card flat bordered>
          <q-card-section class="row items-center no-wrap">
            <q-avatar icon="store" color="green-1" text-color="positive" />
            <div class="q-ml-md">
              <div class="text-h6 text-weight-bold">{{ market.name }}</div>
              <div class="text-caption text-grey-8">{{ market.address || 'No address provided' }}</div>
            </div>
          </q-card-section>

          <q-separator />

          <q-card-actions align="right">
            <q-btn flat color="primary" icon="edit" @click="openMarketDialog(market)" />
            <q-btn flat color="negative" icon="delete" @click="confirmDelete(market)" />
          </q-card-actions>
        </q-card>
      </div>
    </div>

    <q-card v-else flat bordered class="text-center q-pa-lg">
      <q-card-section class="text-grey-7">
        No markets registered in Vitória yet.
      </q-card-section>
    </q-card>

    <q-dialog v-model="marketDialog.show" persistent>
      <q-card style="min-width: 350px">
        <q-card-section>
          <div class="text-h6">{{ marketDialog.id ? 'Edit Market' : 'New Market' }}</div>
        </q-card-section>

        <q-card-section class="q-gutter-md">
          <q-input v-model="marketDialog.name" label="Market Name *" outlined dense />
          <q-input v-model="marketDialog.address" label="Address" outlined dense hint="Ex: Av. Dante Michelini, Vitória" />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" color="grey" v-close-popup />
          <q-btn flat label="Save" color="primary" @click="saveMarket" :loading="marketDialog.loading" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from 'src/boot/axios'
import { useQuasar } from 'quasar'

const $q = useQuasar()
const markets = ref([])
const loading = ref(true)

const marketDialog = ref({
  show: false,
  loading: false,
  id: null,
  name: '',
  address: ''
})

async function fetchMarkets() {
  loading.value = true
  try {
    const response = await api.get('/markets/')
    markets.value = response.data
  } catch {
    $q.notify({ color: 'negative', message: 'Error loading markets' })
  } finally {
    loading.value = false
  }
}

function openMarketDialog(market = null) {
  if (market) {
    marketDialog.value = {
      show: true,
      loading: false,
      id: market.id,
      name: market.name,
      address: market.address || ''
    }
  } else {
    marketDialog.value = {
      show: true,
      loading: false,
      id: null,
      name: '',
      address: ''
    }
  }
}

async function saveMarket() {
  if (!marketDialog.value.name) {
    $q.notify({ color: 'warning', message: 'Name is required' })
    return
  }

  marketDialog.value.loading = true
  try {
    const payload = {
      name: marketDialog.value.name,
      address: marketDialog.value.address
    }

    if (marketDialog.value.id) {
      await api.put(`/markets/${marketDialog.value.id}`, payload)
      $q.notify({ color: 'positive', message: 'Market updated!' })
    } else {
      await api.post('/markets/', payload)
      $q.notify({ color: 'positive', message: 'Market created!' })
    }
    
    marketDialog.value.show = false
    fetchMarkets()
  } catch {
    $q.notify({ color: 'negative', message: 'Error saving market' })
  } finally {
    marketDialog.value.loading = false
  }
}

function confirmDelete(market) {
  $q.dialog({
    title: 'Confirm Deletion',
    message: `Delete "${market.name}"? This might affect price records.`,
    cancel: true,
    persistent: true,
    ok: { color: 'negative', label: 'Delete' }
  }).onOk(async () => {
    try {
      await api.delete(`/markets/${market.id}`)
      $q.notify({ color: 'positive', message: 'Market removed' })
      fetchMarkets()
    } catch {
      $q.notify({ color: 'negative', message: 'Failed to delete market' })
    }
  })
}

onMounted(fetchMarkets)
</script>
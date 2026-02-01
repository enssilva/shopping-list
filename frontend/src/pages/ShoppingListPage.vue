<template>
  <q-page class="q-pa-md">
    <div class="row items-center justify-between q-mb-md">
      <div class="text-h5">My Shopping Lists</div>
      <q-btn color="primary" icon="add" label="New List" to="/create-list" />
    </div>

    <div v-if="loading" class="flex flex-center q-pa-lg">
      <q-spinner-dots color="primary" size="40px" />
    </div>

    <q-card v-else-if="allLists.length === 0" flat bordered class="q-pa-md text-center">
      <q-card-section>
        <q-icon name="playlist_add" size="64px" color="grey-5" />
        <div class="text-h6 text-grey-7">No lists found</div>
        <q-btn label="Create your first list" color="primary" to="/create-list" class="q-mt-md" />
      </q-card-section>
    </q-card>

    <div v-else class="row q-col-gutter-md">
      <div v-for="list in allLists" :key="list.id" class="col-12 col-sm-6 col-md-4">
        <q-card 
          flat 
          bordered 
          class="cursor-pointer hover-shadow" 
          @click="viewListDetails(list.id)"
        >
          <q-card-section>
            <div class="text-h6 text-primary">{{ list.name }}</div>
            <div class="text-caption text-grey">
              Created on: {{ new Date(list.created_at).toLocaleDateString() }}
            </div>
          </q-card-section>

          <q-separator />

          <q-card-section>
            <div class="row items-center">
              <q-icon name="shopping_basket" class="q-mr-xs" />
              <span>{{ list.items?.length || 0 }} products</span>
            </div>
            <div v-if="list.description" class="text-body2 text-grey-8 q-mt-sm">
              {{ list.description }}
            </div>
          </q-card-section>

          <q-card-actions align="right">
            <q-btn flat color="negative" icon="delete" @click.stop="confirmDelete(list)" />
            <q-btn flat color="primary" label="Open List" />
          </q-card-actions>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from 'src/boot/axios'
import { useAuthStore } from 'src/stores/auth'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'

const $q = useQuasar()
const router = useRouter()
const authStore = useAuthStore()
const loading = ref(true)
const allLists = ref([])

async function fetchUserLists() {
  loading.value = true
  try {
    // Correct GET route using path parameter
    const response = await api.get(`/lists/${authStore.userId}`)
    allLists.value = response.data
  } catch {
    $q.notify({ color: 'negative', message: 'Error loading lists' })
  } finally {
    loading.value = false
  }
}

function viewListDetails(listId) {
  // Navigate to a new page to see products inside this specific list
  router.push(`/shopping-list/${listId}`)
}

async function confirmDelete(list) {
  $q.dialog({
    title: 'Delete List',
    message: `Are you sure you want to delete "${list.name}"?`,
    cancel: true,
    persistent: true
  }).onOk(async () => {
    try {
      await api.delete(`/lists/${list.id}`)
      allLists.value = allLists.value.filter(l => l.id !== list.id)
      $q.notify({ color: 'positive', message: 'List removed' })
    } catch {
      $q.notify({ color: 'negative', message: 'Failed to delete' })
    }
  })
}

onMounted(fetchUserLists)
</script>

<style scoped>
.hover-shadow:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  transition: box-shadow 0.3s ease;
}
</style>
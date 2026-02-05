<template>
  <q-page class="q-pa-md bg-grey-1">
    <div class="row items-center q-mb-lg">
      <div class="col">
        <div class="text-h5 text-weight-bold">Olá, {{ authStore.userName.split(' ')[0] }}!</div>
        <div class="text-subtitle2 text-grey-7">O que vamos comprar hoje em Vitória?</div>
      </div>
      <q-avatar size="56px">
        <img src="https://cdn.quasar.dev/img/boy-avatar.png">
      </q-avatar>
    </div>

    <div class="row q-col-gutter-md q-mb-xl">
      <div class="col-6">
        <q-card clickable v-ripple class="text-center q-pa-sm cursor-pointer bg-primary text-white" @click="router.push('/add-product')">
          <q-card-section>
            <q-icon name="barcode_reader" size="md" />
            <div class="text-subtitle2 q-mt-sm">Escanear</div>
          </q-card-section>
        </q-card>
      </div>
      <div class="col-6">
        <q-card clickable v-ripple class="text-center q-pa-sm cursor-pointer bg-secondary text-white" @click="router.push('/shopping-list')">
          <q-card-section>
            <q-icon name="list_alt" size="md" />
            <div class="text-subtitle2 q-mt-sm">Minhas Listas</div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <div class="text-h6 q-mb-sm">Listas Recentes</div>
    <q-list bordered separator class="bg-white rounded-borders">
      <q-item v-if="loading" class="q-pa-md text-center">
        <q-spinner-dots color="primary" size="30px" />
      </q-item>
      
      <q-item v-else-if="recentLists.length === 0" class="text-grey-6 italic">
        Nenhuma lista criada recentemente.
      </q-item>

      <q-item 
        v-for="list in recentLists" 
        :key="list.id" 
        clickable 
        @click="router.push(`/shopping-list/details/${list.id}`)"
      >
        <q-item-section avatar>
          <q-icon name="shopping_basket" color="primary" />
        </q-item-section>
        <q-item-section>
          <q-item-label class="text-weight-bold">{{ list.name }}</q-item-label>
          <q-item-label caption>{{ list.items?.length || 0 }} produtos</q-item-label>
        </q-item-section>
        <q-item-section side>
          <q-icon name="chevron_right" />
        </q-item-section>
      </q-item>
    </q-list>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from 'src/boot/axios'
import { useAuthStore } from 'src/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const recentLists = ref([])
const loading = ref(true)

async function fetchRecentLists() {
  try {
    // Busca as listas do usuário logado
    const response = await api.get(`/lists/${authStore.userId}`)
    recentLists.value = response.data.slice(0, 5) // Mostra apenas as 5 últimas
  } catch (error) {
    console.error('Falha ao carregar listas:', error)
  } finally {
    loading.value = false
  }
}

onMounted(fetchRecentLists)
</script>
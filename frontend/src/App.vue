<template>
  <router-view v-if="!authStore.loading" />
  
  <div v-else class="flex flex-center" style="height: 100vh">
    <q-spinner-dots color="primary" size="40px" />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from 'src/stores/auth'

const authStore = useAuthStore()

onMounted(async () => {
  // Verifica se existe um token salvo no localStorage de Vitória
  const token = localStorage.getItem('access_token')
  
  if (token) {
    try {
      // Dispara a action que criámos no auth.js
      // Esta action chamará a rota /me no backend FastAPI
      await authStore.restoreSession()
    } catch (error) {
      console.error('Sessão expirada:', error)
    }
  }
})
</script>
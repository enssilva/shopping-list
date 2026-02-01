<template>
  <q-page class="flex flex-center">
    <q-btn 
      label="Testar Conexão API" 
      color="primary" 
      @click="testConnection" 
    />
    
    <div v-if="apiResponse" class="q-mt-md">
      Status: <q-badge color="green">Conectado!</q-badge>
      <pre>{{ apiResponse }}</pre>
    </div>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import { api } from 'src/boot/axios'

const apiResponse = ref(null)

async function testConnection() {
  try {
    // This will call http://localhost:8000/api/v1/markets/
    const response = await api.get('/markets/')
    apiResponse.value = response.data
    console.log('API Response:', response.data)
  } catch (error) {
    console.error('Connection failed:', error)
    apiResponse.value = 'Erro ao conectar: ' + error.message
  }
}
</script>